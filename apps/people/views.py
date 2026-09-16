import openpyxl
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse
from .forms import EmployeeForm, ExcelImportForm
from .models import Department, Designation, Employee
from django.utils import timezone
from django.core.exceptions import PermissionDenied

from .forms import ContactDetailsForm, ContactImportForm
from .models import ContactDetails

STATUS_LOOKUP = {label.upper(): code for code, label in Employee.STATUS_CHOICES}
EMPLOYMENT_TYPE_LOOKUP = {
    label.upper(): code for code, label in Employee.EMPLOYMENT_TYPE_CHOICES
}
EMPLOYEE_CATEGORY_LOOKUP = {
    label.upper(): code for code, label in Employee.EMPLOYEE_CATEGORY_CHOICES
}
INITIAL_LOOKUP = {label.upper(): code for code, label in Employee.INITIAL_CHOICES}


SORT_FIELD_MAP = {
    "employee_id": "employee_id",
    "full_name": "full_name",
    "department": "department__name",
    "designation": "designation__name",
    "status": "status",
    "employment_type": "employment_type",
    "employee_category": "employee_category",
}


def _get_filtered_sorted_employees(request):
    """Shared by the Employee list page and the Excel export, so both
    always show/export exactly the same set of employees for a given
    set of filters, search text, and sort order."""
    employees = Employee.objects.select_related("department", "designation").all()

    query = request.GET.get("q", "").strip()
    if query:
        employees = employees.filter(full_name__icontains=query) | employees.filter(
            employee_id__icontains=query
        )

    department = request.GET.get("department", "").strip()
    if department:
        employees = employees.filter(department_id=department)

    designation = request.GET.get("designation", "").strip()
    if designation:
        employees = employees.filter(designation_id=designation)

    status = request.GET.get("status", "").strip()
    if status:
        employees = employees.filter(status=status)

    employment_type = request.GET.get("employment_type", "").strip()
    if employment_type:
        employees = employees.filter(employment_type=employment_type)

    employees = employees.distinct()

    sort_field = request.GET.get("sort", "full_name")
    sort_dir = request.GET.get("dir", "asc")
    order_column = SORT_FIELD_MAP.get(sort_field, "full_name")
    if sort_dir == "desc":
        order_column = "-" + order_column

    return employees.order_by(order_column)


@login_required
def employee_list(request):
    employees = _get_filtered_sorted_employees(request)
    context = {
        "employees": employees,
        "query": request.GET.get("q", "").strip(),
        "selected_department": request.GET.get("department", "").strip(),
        "selected_designation": request.GET.get("designation", "").strip(),
        "selected_status": request.GET.get("status", "").strip(),
        "selected_employment_type": request.GET.get("employment_type", "").strip(),
        "departments": Department.objects.filter(is_active=True),
        "designations": Designation.objects.filter(is_active=True),
        "status_choices": Employee.STATUS_CHOICES,
        "employment_type_choices": Employee.EMPLOYMENT_TYPE_CHOICES,
    }
    return render(request, "people/employee_list.html", context)

@login_required
@permission_required("people.view_employee", raise_exception=True)
def employee_export(request):
    """Exports employees to Excel. If specific rows were checked on the
    list page, only those are exported; otherwise everything currently
    matching the filters/search/sort is exported."""

    employees = _get_filtered_sorted_employees(request)

    selected_ids = request.GET.getlist("selected_ids")
    if selected_ids:
        employees = employees.filter(pk__in=selected_ids)

    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Employees"

    headers = [
        "Employee ID", "Initial", "Name", "Department", "Designation",
        "Status", "Employment Type", "Employee Category", "Date Joined",
    ]
    sheet.append(headers)

    for employee in employees:
        sheet.append([
            employee.employee_id,
            employee.get_initial_display() if employee.initial else "",
            employee.full_name,
            employee.department.name,
            employee.designation.name,
            employee.get_status_display(),
            employee.get_employment_type_display(),
            employee.get_employee_category_display(),
            employee.date_joined.strftime("%Y-%m-%d") if employee.date_joined else "",
        ])

    for column_cells in sheet.columns:
        max_length = max(len(str(cell.value)) for cell in column_cells)
        sheet.column_dimensions[column_cells[0].column_letter].width = max_length + 4

    timestamp = timezone.now().strftime("%Y-%m-%d_%H%M")
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = f'attachment; filename="employees_export_{timestamp}.xlsx"'
    workbook.save(response)
    return response


@login_required
def employee_detail(request, pk):
    employee = get_object_or_404(
        Employee.objects.select_related("department", "designation"), pk=pk
    )
    return render(request, "people/employee_detail.html", {"employee": employee})


@login_required
@permission_required("people.add_employee", raise_exception=True)
def employee_add(request):
    if request.method == "POST":
        form = EmployeeForm(request.POST)
        if form.is_valid():
            employee = form.save()
            messages.success(request, f"Employee {employee.full_name} was added.")
            return redirect("people:employee_detail", pk=employee.pk)
    else:
        form = EmployeeForm()
    return render(request, "people/employee_form.html", {"form": form, "title": "Add Employee"})


@login_required
@permission_required("people.change_employee", raise_exception=True)
def employee_edit(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == "POST":
        form = EmployeeForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            messages.success(request, f"Employee {employee.full_name} was updated.")
            return redirect("people:employee_detail", pk=employee.pk)
    else:
        form = EmployeeForm(instance=employee)
    return render(request, "people/employee_form.html", {"form": form, "title": "Edit Employee"})


@login_required
@permission_required("people.delete_employee", raise_exception=True)
def employee_delete(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == "POST":
        name = employee.full_name
        employee.delete()
        messages.success(request, f"Employee {name} was permanently deleted.")
        return redirect("people:employee_list")
    return render(request, "people/employee_confirm_delete.html", {"employee": employee})


@login_required
@permission_required("people.add_employee", raise_exception=True)
def employee_import(request):
    results = None
    if request.method == "POST":
        form = ExcelImportForm(request.POST, request.FILES)
        if form.is_valid():
            results = _process_excel_import(request.FILES["excel_file"])
    else:
        form = ExcelImportForm()
    return render(request, "people/employee_import.html", {"form": form, "results": results})


def _process_excel_import(uploaded_file):
    """Reads an uploaded Excel file and creates one Employee per valid row,
    running each row through the exact same EmployeeForm used by the web
    page — see the class docstring in forms.py."""

    workbook = openpyxl.load_workbook(uploaded_file, data_only=True)
    sheet = workbook.active

    header_row = [str(cell.value).strip() if cell.value else "" for cell in sheet[1]]
    required_headers = [
        "Employee ID",
        "Name",
        "Department",
        "Designation",
        "Status",
        "Employment Type",
        "Employee Category",
    ]
    optional_headers = ["Initial", "Date Joined"]

    missing = [h for h in required_headers if h not in header_row]
    if missing:
        return {
            "success_count": 0,
            "errors": [f"The Excel file is missing required column(s): {', '.join(missing)}"],
        }

    col_index = {name: header_row.index(name) for name in required_headers}
    for name in optional_headers:
        if name in header_row:
            col_index[name] = header_row.index(name)

    success_count = 0
    errors = []

    for row_number, row in enumerate(sheet.iter_rows(min_row=2), start=2):
        values = [cell.value for cell in row]
        if all(v is None or str(v).strip() == "" for v in values):
            continue  # skip blank rows

        raw_employee_id = str(values[col_index["Employee ID"]] or "").strip()
        raw_full_name = str(values[col_index["Name"]] or "").strip()
        raw_department = str(values[col_index["Department"]] or "").strip()
        raw_designation = str(values[col_index["Designation"]] or "").strip()
        raw_status = str(values[col_index["Status"]] or "").strip()
        raw_employment_type = str(values[col_index["Employment Type"]] or "").strip()
        raw_employee_category = str(values[col_index["Employee Category"]] or "").strip()

        raw_initial = ""
        if "Initial" in col_index:
            raw_initial = str(values[col_index["Initial"]] or "").strip()

        raw_date_joined = None
        if "Date Joined" in col_index:
            raw_date_joined = values[col_index["Date Joined"]]

        department = Department.objects.filter(name__iexact=raw_department).first()
        designation = Designation.objects.filter(name__iexact=raw_designation).first()

        row_errors = []
        if not department:
            row_errors.append(
                f"Department '{raw_department}' does not exist yet — add it via the admin panel first."
            )
        if not designation:
            row_errors.append(
                f"Designation '{raw_designation}' does not exist yet — add it via the admin panel first."
            )

        status_code = STATUS_LOOKUP.get(raw_status.upper())
        if not status_code:
            row_errors.append(f"Status '{raw_status}' is not a recognized option.")

        employment_type_code = EMPLOYMENT_TYPE_LOOKUP.get(raw_employment_type.upper())
        if not employment_type_code:
            row_errors.append(f"Employment Type '{raw_employment_type}' is not a recognized option.")

        employee_category_code = EMPLOYEE_CATEGORY_LOOKUP.get(raw_employee_category.upper())
        if not employee_category_code:
            row_errors.append(f"Employee Category '{raw_employee_category}' is not a recognized option.")

        initial_code = ""
        if raw_initial:
            initial_code = INITIAL_LOOKUP.get(raw_initial.upper())
            if not initial_code:
                row_errors.append(f"Initial '{raw_initial}' is not a recognized option.")

        date_joined_value = None
        if raw_date_joined not in (None, ""):
            date_joined_value = (
                raw_date_joined.date() if hasattr(raw_date_joined, "date") else raw_date_joined
            )

        if row_errors:
            errors.append(f"Row {row_number}: " + " ".join(row_errors))
            continue

        form = EmployeeForm(
            data={
                "employee_id": raw_employee_id,
                "initial": initial_code,
                "full_name": raw_full_name,
                "department": department.pk,
                "designation": designation.pk,
                "status": status_code,
                "date_joined": date_joined_value,
                "employment_type": employment_type_code,
                "employee_category": employee_category_code,
            }
        )
        if form.is_valid():
            form.save()
            success_count += 1
        else:
            field_errors = "; ".join(
                f"{field}: {', '.join(msgs)}" for field, msgs in form.errors.items()
            )
            errors.append(f"Row {row_number} ({raw_employee_id or 'blank ID'}): {field_errors}")

    return {"success_count": success_count, "errors": errors}

@login_required
def contact_details_edit(request, employee_id):
    employee = get_object_or_404(Employee, pk=employee_id)
    contact = getattr(employee, "contact_details", None)

    required_perm = "people.change_contactdetails" if contact else "people.add_contactdetails"
    if not request.user.has_perm(required_perm):
        raise PermissionDenied

    if request.method == "POST":
        form = ContactDetailsForm(request.POST, instance=contact)
        if form.is_valid():
            contact_obj = form.save(commit=False)
            contact_obj.employee = employee
            contact_obj.save()
            messages.success(request, "Contact details saved.")
            return redirect("people:employee_detail", pk=employee.pk)
    else:
        form = ContactDetailsForm(instance=contact)

    return render(
        request,
        "people/contact_details_form.html",
        {"form": form, "employee": employee, "is_edit": contact is not None},
    )


@login_required
@permission_required("people.delete_contactdetails", raise_exception=True)
def contact_details_delete(request, employee_id):
    employee = get_object_or_404(Employee, pk=employee_id)
    contact = get_object_or_404(ContactDetails, employee=employee)
    if request.method == "POST":
        contact.delete()
        messages.success(request, "Contact details were permanently deleted.")
        return redirect("people:employee_detail", pk=employee.pk)
    return render(
        request, "people/contact_confirm_delete.html", {"employee": employee}
    )

@login_required
def contact_import_template(request):
    """Gives the user a ready-to-fill Excel file with the correct column
    headings and one example row, so they don't have to guess the format
    before using the Contact Details importer above."""

    if not (
        request.user.has_perm("people.add_contactdetails")
        and request.user.has_perm("people.change_contactdetails")
    ):
        raise PermissionDenied

    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Contact Details"

    headers = [
        "Employee ID", "Personal Mobile", "Alternate Mobile", "Personal Email",
        "Official Email", "Current Address", "Permanent Address",
        "Emergency Contact Name", "Emergency Contact Phone", "Emergency Contact Relation",
    ]
    sheet.append(headers)
    sheet.append([
        "EMP001", "9876543210", "9123456780", "employee@example.com",
        "employee@university.edu", "123 Example Street, City",
        "123 Example Street, City", "Jane Doe", "9988776655", "Spouse",
    ])

    for column_cells in sheet.columns:
        max_length = max(len(str(cell.value)) for cell in column_cells)
        sheet.column_dimensions[column_cells[0].column_letter].width = max_length + 4

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = 'attachment; filename="contact_details_import_template.xlsx"'
    workbook.save(response)
    return response


@login_required
def contact_import(request):
    if not (
        request.user.has_perm("people.add_contactdetails")
        and request.user.has_perm("people.change_contactdetails")
    ):
        raise PermissionDenied

    results = None
    if request.method == "POST":
        form = ContactImportForm(request.POST, request.FILES)
        if form.is_valid():
            results = _process_contact_excel_import(request.FILES["excel_file"])
    else:
        form = ContactImportForm()
    return render(request, "people/contact_import.html", {"form": form, "results": results})


def _process_contact_excel_import(uploaded_file):
    """Reads an uploaded Excel file and adds/updates one ContactDetails
    record per matching Employee ID. The employee must already exist —
    this importer never creates new employees, only their contact info."""

    workbook = openpyxl.load_workbook(uploaded_file, data_only=True)
    sheet = workbook.active

    header_row = [str(cell.value).strip() if cell.value else "" for cell in sheet[1]]
    required_headers = [
        "Employee ID", "Personal Mobile", "Alternate Mobile", "Personal Email",
        "Official Email", "Current Address", "Permanent Address",
        "Emergency Contact Name", "Emergency Contact Phone", "Emergency Contact Relation",
    ]
    missing = [h for h in required_headers if h not in header_row]
    if missing:
        return {
            "success_count": 0,
            "errors": [f"The Excel file is missing required column(s): {', '.join(missing)}"],
        }

    col_index = {name: header_row.index(name) for name in required_headers}
    success_count = 0
    errors = []

    for row_number, row in enumerate(sheet.iter_rows(min_row=2), start=2):
        values = [cell.value for cell in row]
        if all(v is None or str(v).strip() == "" for v in values):
            continue

        employee_id = str(values[col_index["Employee ID"]] or "").strip()
        employee = Employee.objects.filter(employee_id__iexact=employee_id).first()
        if not employee:
            errors.append(f"Row {row_number}: Employee ID '{employee_id}' was not found.")
            continue

        existing_contact = getattr(employee, "contact_details", None)
        form_data = {
            "personal_mobile": str(values[col_index["Personal Mobile"]] or "").strip(),
            "alternate_mobile": str(values[col_index["Alternate Mobile"]] or "").strip(),
            "personal_email": str(values[col_index["Personal Email"]] or "").strip(),
            "official_email": str(values[col_index["Official Email"]] or "").strip(),
            "current_address": str(values[col_index["Current Address"]] or "").strip(),
            "permanent_address": str(values[col_index["Permanent Address"]] or "").strip(),
            "emergency_contact_name": str(values[col_index["Emergency Contact Name"]] or "").strip(),
            "emergency_contact_phone": str(values[col_index["Emergency Contact Phone"]] or "").strip(),
            "emergency_contact_relation": str(values[col_index["Emergency Contact Relation"]] or "").strip(),
        }

        form = ContactDetailsForm(data=form_data, instance=existing_contact)
        if form.is_valid():
            contact_obj = form.save(commit=False)
            contact_obj.employee = employee
            contact_obj.save()
            success_count += 1
        else:
            field_errors = "; ".join(
                f"{field}: {', '.join(msgs)}" for field, msgs in form.errors.items()
            )
            errors.append(f"Row {row_number} ({employee_id}): {field_errors}")

    return {"success_count": success_count, "errors": errors}