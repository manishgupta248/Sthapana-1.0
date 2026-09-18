from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from .models import Document, DocumentCategory, Tag


@admin.register(DocumentCategory)
class DocumentCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "folder_name", "is_active"]
    list_filter = ["is_active"]
    search_fields = ["name"]


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ["name"]
    search_fields = ["name"]


@admin.register(Document)
class DocumentAdmin(SimpleHistoryAdmin):
    list_display = ["title", "category", "document_date", "uploaded_by", "is_deleted", "file_size_display"]
    list_filter = ["category", "is_deleted", "document_date"]
    search_fields = ["title", "description", "original_filename"]
    filter_horizontal = ["tags"]
    readonly_fields = ["original_filename", "file_type", "file_size", "uploaded_at"]