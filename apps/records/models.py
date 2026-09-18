import os
import shutil

from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils import timezone
from simple_history.models import HistoricalRecords

from .storage import document_storage, document_upload_path


class DocumentCategory(models.Model):
    """Managed lookup list, same pattern as Department/Designation
    (DECISIONS.md #19) — admin-managed, not free text, so the physical
    folder structure stays predictable."""
    name = models.CharField(max_length=100, unique=True)
    folder_name = models.CharField(
        max_length=100, unique=True,
        help_text="Must exactly match a real folder name under the document store.",
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Document categories"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Document(models.Model):
    title = models.CharField(
        max_length=255,
        help_text="Also used to build the saved file's standard name.",
    )
    category = models.ForeignKey(DocumentCategory, on_delete=models.PROTECT, related_name="documents")
    tags = models.ManyToManyField(Tag, blank=True, related_name="documents")
    document_date = models.DateField(default=timezone.localdate)
    description = models.TextField(blank=True)

    file = models.FileField(
        upload_to=document_upload_path,
        storage=document_storage,
        validators=[FileExtensionValidator(allowed_extensions=settings.ALLOWED_DOCUMENT_EXTENSIONS)],
    )
    original_filename = models.CharField(max_length=255, editable=False)
    file_type = models.CharField(max_length=20, editable=False)
    file_size = models.PositiveIntegerField(editable=False, help_text="Bytes")

    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="uploaded_documents"
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="deleted_documents",
    )

    def save(self, *args, **kwargs):
        """Auto-fills file metadata; for a brand-new document, renames
        the file to its final standard name once the ID exists; for an
        existing document whose category changed, moves the physical
        file into the new category's folder to match."""
        is_new = self.pk is None
        old_category_id = None
        if not is_new:
            old_category_id = Document.objects.filter(pk=self.pk).values_list("category_id", flat=True).first()

        if self.file and not self.original_filename:
            self.original_filename = os.path.basename(self.file.name)
        if self.file and not self.file_size:
            self.file_size = self.file.size
        if self.file and not self.file_type:
            self.file_type = os.path.splitext(self.original_filename or self.file.name)[1].lstrip(".").lower()

        super().save(*args, **kwargs)

        if is_new and self.file:
            self._finalize_filename()
        elif not is_new and old_category_id is not None and old_category_id != self.category_id:
            self._move_to_current_category()

    def _finalize_filename(self):
        """Moves the file from its temporary upload name to the final
        standard name, now that self.pk exists."""
        old_path = self.file.path
        new_relative = document_upload_path(self, self.original_filename)
        new_path = os.path.join(settings.DOCUMENT_STORE_ROOT, new_relative)

        os.makedirs(os.path.dirname(new_path), exist_ok=True)
        if os.path.exists(old_path) and old_path != new_path:
            shutil.move(old_path, new_path)

        self.file.name = new_relative
        super().save(update_fields=["file"])

    def _move_to_current_category(self):
        """Relocates the physical file into the new category's folder
        (keeping the same filename) after an edit changes the category,
        so the file's real location always matches what the database says."""
        if not self.file or self.is_deleted:
            return
        old_path = self.file.path
        filename = os.path.basename(self.file.name)
        new_relative = f"{self.category.folder_name}/{filename}"
        new_path = os.path.join(settings.DOCUMENT_STORE_ROOT, new_relative)

        os.makedirs(os.path.dirname(new_path), exist_ok=True)
        if os.path.exists(old_path) and old_path != new_path:
            shutil.move(old_path, new_path)

        self.file.name = new_relative
        super().save(update_fields=["file"])

    history = HistoricalRecords()

    class Meta:
        ordering = ["-document_date", "-uploaded_at"]

    def __str__(self):
        return self.title

    @property
    def file_size_display(self):
        size = self.file_size or 0
        if size < 1024:
            return f"{size} B"
        if size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        return f"{size / (1024 * 1024):.1f} MB"

    def soft_delete(self, user):
        """Moves the physical file to the trash folder (mirroring its
        category subfolder) and marks the record deleted. Recoverable
        via restore() — see Django admin."""
        if self.is_deleted:
            return
        if self.file and os.path.exists(self.file.path):
            trash_path = os.path.join(settings.DOCUMENT_TRASH_ROOT, self.file.name)
            os.makedirs(os.path.dirname(trash_path), exist_ok=True)
            shutil.move(self.file.path, trash_path)
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.deleted_by = user
        self.save(update_fields=["is_deleted", "deleted_at", "deleted_by"])

    def restore(self):
        """Moves the file back from trash and un-marks it deleted."""
        if not self.is_deleted:
            return
        trash_path = os.path.join(settings.DOCUMENT_TRASH_ROOT, self.file.name)
        original_path = os.path.join(settings.DOCUMENT_STORE_ROOT, self.file.name)
        if os.path.exists(trash_path):
            os.makedirs(os.path.dirname(original_path), exist_ok=True)
            shutil.move(trash_path, original_path)
        self.is_deleted = False
        self.deleted_at = None
        self.deleted_by = None
        self.save(update_fields=["is_deleted", "deleted_at", "deleted_by"])