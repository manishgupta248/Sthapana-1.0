from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from .models import Document, DocumentCategory, Tag
from .utils import generate_document_filename, resolve_tags

User = get_user_model()


class DocumentCategoryTests(TestCase):
    def test_seeded_categories_exist(self):
        expected = {
            "Notices_and_Circulars", "Booklets", "Financial_Records",
            "Policy_Documents", "Miscellaneous",
        }
        actual = set(DocumentCategory.objects.values_list("folder_name", flat=True))
        self.assertTrue(expected.issubset(actual))


class TagResolutionTests(TestCase):
    def test_resolve_tags_creates_new_tags(self):
        tags = resolve_tags(Tag, "budget, 2026, confidential")
        self.assertEqual(len(tags), 3)
        self.assertEqual(Tag.objects.count(), 3)

    def test_resolve_tags_reuses_existing_case_insensitively(self):
        Tag.objects.create(name="Budget")
        tags = resolve_tags(Tag, "BUDGET, new-tag")
        self.assertEqual(Tag.objects.count(), 2)
        self.assertIn("Budget", [t.name for t in tags])

    def test_resolve_tags_handles_empty_string(self):
        self.assertEqual(resolve_tags(Tag, ""), [])

    def test_resolve_tags_deduplicates_within_input(self):
        tags = resolve_tags(Tag, "budget, Budget, BUDGET")
        self.assertEqual(len(tags), 1)


class DocumentModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="clerk1", password="testpass123")
        self.category = DocumentCategory.objects.get(folder_name="Miscellaneous")

    def _make_document(self, title="Test Document"):
        file = SimpleUploadedFile("original_name.pdf", b"fake pdf content", content_type="application/pdf")
        return Document.objects.create(
            title=title, category=self.category, document_date=date.today(),
            file=file, uploaded_by=self.user,
        )

    def test_file_metadata_auto_filled_on_save(self):
        document = self._make_document()
        self.assertEqual(document.original_filename, "original_name.pdf")
        self.assertEqual(document.file_type, "pdf")
        self.assertGreater(document.file_size, 0)

    def test_filename_renamed_to_standard_pattern(self):
        document = self._make_document(title="Annual Report")
        stored_name = document.file.name.split("/")[-1]
        self.assertIn(str(date.today()), stored_name)
        self.assertIn(f"DOC{document.pk:05d}", stored_name)
        self.assertNotIn("original_name", stored_name)

    def test_generate_document_filename_slugifies_title(self):
        document = self._make_document(title="Meeting Notes: Q1 Review!")
        stored_name = document.file.name.split("/")[-1]
        self.assertNotIn(" ", stored_name)
        self.assertNotIn(":", stored_name)

    def test_soft_delete_marks_and_moves_file(self):
        document = self._make_document()
        document.soft_delete(self.user)
        self.assertTrue(document.is_deleted)
        self.assertEqual(document.deleted_by, self.user)
        self.assertIsNotNone(document.deleted_at)

    def test_default_document_date_is_today_when_omitted(self):
        file = SimpleUploadedFile("f.pdf", b"content", content_type="application/pdf")
        document = Document(title="No Date Given", category=self.category, file=file, uploaded_by=self.user)
        document.full_clean(exclude=["file", "original_filename", "file_type", "file_size"])
        document.save()
        self.assertEqual(document.document_date, date.today())


class DocumentViewPermissionTests(TestCase):
    def setUp(self):
        self.category = DocumentCategory.objects.get(folder_name="Miscellaneous")
        self.viewer = User.objects.create_user(username="readonly1", password="testpass123")
        self.viewer.user_permissions.add(Permission.objects.get(codename="view_document"))

        self.editor = User.objects.create_user(username="clerk1", password="testpass123")
        for codename in ["view_document", "add_document", "change_document"]:
            self.editor.user_permissions.add(Permission.objects.get(codename=codename))

        file = SimpleUploadedFile("f.pdf", b"content", content_type="application/pdf")
        self.document = Document.objects.create(
            title="Permission Test Doc", category=self.category, document_date=date.today(),
            file=file, uploaded_by=self.editor,
        )

    def test_readonly_user_can_view_list(self):
        self.client.force_login(self.viewer)
        response = self.client.get(reverse("records:document_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Permission Test Doc")

    def test_readonly_user_cannot_access_delete(self):
        self.client.force_login(self.viewer)
        response = self.client.get(reverse("records:document_delete", args=[self.document.pk]))
        self.assertEqual(response.status_code, 403)

    def test_readonly_user_cannot_access_edit(self):
        self.client.force_login(self.viewer)
        response = self.client.get(reverse("records:document_edit", args=[self.document.pk]))
        self.assertEqual(response.status_code, 403)

    def test_editor_can_edit_but_not_delete(self):
        self.client.force_login(self.editor)
        response = self.client.get(reverse("records:document_edit", args=[self.document.pk]))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse("records:document_delete", args=[self.document.pk]))
        self.assertEqual(response.status_code, 403)

    def test_deleted_document_excluded_from_list(self):
        self.document.soft_delete(self.editor)
        self.client.force_login(self.viewer)
        response = self.client.get(reverse("records:document_list"))
        self.assertNotContains(response, "Permission Test Doc")

    def test_deleted_document_detail_returns_404(self):
        self.document.soft_delete(self.editor)
        self.client.force_login(self.viewer)
        response = self.client.get(reverse("records:document_detail", args=[self.document.pk]))
        self.assertEqual(response.status_code, 404)


class DocumentListFilterTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="clerk1", password="testpass123")
        self.user.user_permissions.add(Permission.objects.get(codename="view_document"))
        self.cat_a = DocumentCategory.objects.get(folder_name="Booklets")
        self.cat_b = DocumentCategory.objects.get(folder_name="Financial_Records")

        Document.objects.create(
            title="Budget Booklet", category=self.cat_a, document_date=date.today(),
            file=SimpleUploadedFile("a.pdf", b"x", content_type="application/pdf"), uploaded_by=self.user,
        )
        Document.objects.create(
            title="Financial Statement", category=self.cat_b, document_date=date.today() - timedelta(days=10),
            file=SimpleUploadedFile("b.pdf", b"x", content_type="application/pdf"), uploaded_by=self.user,
        )

    def test_text_search_filters_by_title(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("records:document_list"), {"q": "Budget"})
        self.assertContains(response, "Budget Booklet")
        self.assertNotContains(response, "Financial Statement")

    def test_category_filter(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("records:document_list"), {"category": self.cat_b.pk})
        self.assertContains(response, "Financial Statement")
        self.assertNotContains(response, "Budget Booklet")

    def test_date_range_filter(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("records:document_list"), {"date_from": date.today().isoformat()})
        self.assertContains(response, "Budget Booklet")
        self.assertNotContains(response, "Financial Statement")