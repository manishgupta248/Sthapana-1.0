from django import forms
from django.conf import settings
from django.utils import timezone

from .models import Document, DocumentCategory


class DocumentUploadForm(forms.ModelForm):
    tags = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "e.g. budget, 2026, confidential",
        }),
        help_text="Comma-separated. Existing tags are reused automatically.",
    )

    class Meta:
        model = Document
        fields = ["title", "category", "document_date", "description", "file"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "category": forms.Select(attrs={"class": "form-select"}),
            "document_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "description": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
            "file": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["category"].queryset = DocumentCategory.objects.filter(is_active=True)
        self.fields["document_date"].required = False

    def clean_document_date(self):
        return self.cleaned_data.get("document_date") or timezone.localdate()

    def clean_file(self):
        file = self.cleaned_data["file"]
        max_bytes = settings.MAX_DOCUMENT_UPLOAD_MB * 1024 * 1024
        if file.size > max_bytes:
            raise forms.ValidationError(
                f"File is too large. Maximum size is {settings.MAX_DOCUMENT_UPLOAD_MB} MB."
            )
        return file

class DocumentEditForm(forms.ModelForm):
    tags = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. budget, 2026, confidential"}),
        help_text="Comma-separated. Existing tags are reused automatically.",
    )

    class Meta:
        model = Document
        fields = ["title", "category", "document_date", "description"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "category": forms.Select(attrs={"class": "form-select"}),
            "document_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "description": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["category"].queryset = DocumentCategory.objects.filter(is_active=True)
        if self.instance.pk:
            self.fields["tags"].initial = ", ".join(self.instance.tags.values_list("name", flat=True))