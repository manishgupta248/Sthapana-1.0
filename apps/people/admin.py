from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from .models import Department, Designation, Employee, ContactDetails
import openpyxl
from django.shortcuts import render
from django.urls import path

from .forms import LookupImportForm

class ExcelImportAdminMixin:
    """Adds an 'Import from Excel' button and page to a ModelAdmin, for
    simple two-column lookup tables (Name + Is Active). Shared by
    DepartmentAdmin and DesignationAdmin below since both tables have the
    exact same shape."""

    change_list_template = "admin/people/lookup_change_list.html"

    def get_urls(self):
        custom_urls = [
            path(
                "import-excel/",
                self.admin_site.admin_view(self.import_excel_view),
                name=f"{self.model._meta.app_label}_{self.model._meta.model_name}_import_excel",
            ),
        ]
        return custom_urls + super().get_urls()

    def import_excel_view(self, request):
        results = None
        if request.method == "POST":
            form = LookupImportForm(request.POST, request.FILES)
            if form.is_valid():
                results = self._process_lookup_import(request.FILES["excel_file"])
        else:
            form = LookupImportForm()

        context = {
            **self.admin_site.each_context(request),
            "form": form,
            "results": results,
            "title": f"Import {self.model._meta.verbose_name_plural} from Excel",
            "opts": self.model._meta,
        }
        return render(request, "admin/people/import_lookup.html", context)

    def _process_lookup_import(self, uploaded_file):
        workbook = openpyxl.load_workbook(uploaded_file, data_only=True)
        sheet = workbook.active

        header_row = [str(cell.value).strip() if cell.value else "" for cell in sheet[1]]
        if "Name" not in header_row:
            return {
                "success_count": 0, "skipped": [],
                "errors": ["The Excel file must have a 'Name' column."],
            }

        name_col = header_row.index("Name")
        active_col = header_row.index("Is Active") if "Is Active" in header_row else None

        success_count = 0
        skipped = []
        errors = []

        for row_number, row in enumerate(sheet.iter_rows(min_row=2), start=2):
            values = [cell.value for cell in row]
            if all(v is None or str(v).strip() == "" for v in values):
                continue

            name = str(values[name_col] or "").strip()
            if not name:
                errors.append(f"Row {row_number}: Name is blank.")
                continue

            is_active = True
            if active_col is not None:
                raw_active = str(values[active_col] or "").strip().lower()
                if raw_active in ("no", "n", "false", "0"):
                    is_active = False

            if self.model.objects.filter(name__iexact=name).exists():
                skipped.append(f"Row {row_number}: '{name}' already exists — skipped.")
                continue

            self.model.objects.create(name=name, is_active=is_active)
            success_count += 1

        return {"success_count": success_count, "skipped": skipped, "errors": errors}

@admin.register(Department)
class DepartmentAdmin(ExcelImportAdminMixin, admin.ModelAdmin):
    list_display = ["name", "is_active"]
    search_fields = ["name"]


@admin.register(Designation)
class DesignationAdmin(ExcelImportAdminMixin, admin.ModelAdmin):
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
        "employee_category",
        "date_joined",
    ]
    list_filter = ["status", "employment_type", "employee_category", "department"]
    search_fields = ["employee_id", "full_name"]

@admin.register(ContactDetails)
class ContactDetailsAdmin(SimpleHistoryAdmin):
    list_display = ["employee", "personal_mobile", "official_email"]
    search_fields = ["employee__full_name", "employee__employee_id"]