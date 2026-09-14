from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from .models import Task, TaskAttachment


class TaskAttachmentInline(admin.TabularInline):
    model = TaskAttachment
    extra = 0
    exclude = ("uploaded_by",)


@admin.register(Task)
class TaskAdmin(SimpleHistoryAdmin):
    list_display = ("title", "assignee", "due_date", "status", "priority", "is_overdue")
    list_filter = ("status", "priority")
    search_fields = ("title", "description")
    inlines = [TaskAttachmentInline]
    exclude = ("created_by",)

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            if isinstance(instance, TaskAttachment):
                instance.uploaded_by = request.user
            instance.save()
        formset.save_m2m()