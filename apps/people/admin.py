from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from .models import Department, Designation, Employee, ContactDetails


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ["name", "is_active"]
    search_fields = ["name"]


@admin.register(Designation)
class DesignationAdmin(admin.ModelAdmin):
    list_display = ["name", "is_active"]
    search_fields = ["name"]


@admin.register(Employee)
class EmployeeAdmin(SimpleHistoryAdmin):
    list_display = [
        "employee_id",
        "full_name",
        "department",
        "designation",
        "status",
        "employment_type",
        "date_joined",
    ]
    list_filter = ["status", "employment_type", "department"]
    search_fields = ["employee_id", "full_name"]

@admin.register(ContactDetails)
class ContactDetailsAdmin(SimpleHistoryAdmin):
    list_display = ["employee", "personal_mobile", "official_email"]
    search_fields = ["employee__full_name", "employee__employee_id"]