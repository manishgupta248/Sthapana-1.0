import openpyxl
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import EmployeeForm, ExcelImportForm
from .models import Department, Designation, Employee

STATUS_LOOKUP = {label.upper(): code for code, label in Employee.STATUS_CHOICES}
EMPLOYMENT_TYPE_LOOKUP = {
    label.upper(): code for code, label in Employee.EMPLOYMENT_TYPE_CHOICES
}


@login_required
def employee_list(request):
    employees = Employee.objects.select_related("department", "designation").all()
    query = request.GET.get("q", "").strip()
    if query:
        employees = employees.filter(full_name__icontains=query) | employees.filter(
            employee_id__icontains=query
        )
    return render(
        request, "people/employee_list.html", {"employees": employees, "query": query}
    )


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
        "Full Name",
        "Department",
        "Designation",
        "Status",
        "Date Joined",
        "Employment Type",
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
            continue  # skip blank rows

        raw_employee_id = str(values[col_index["Employee ID"]] or "").strip()
        raw_full_name = str(values[col_index["Full Name"]] or "").strip()
        raw_department = str(values[col_index["Department"]] or "").strip()
        raw_designation = str(values[col_index["Designation"]] or "").strip()
        raw_status = str(values[col_index["Status"]] or "").strip()
        raw_date_joined = values[col_index["Date Joined"]]
        raw_employment_type = str(values[col_index["Employment Type"]] or "").strip()

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

        date_joined_value = (
            raw_date_joined.date() if hasattr(raw_date_joined, "date") else raw_date_joined
        )

        if row_errors:
            errors.append(f"Row {row_number}: " + " ".join(row_errors))
            continue

        form = EmployeeForm(
            data={
                "employee_id": raw_employee_id,
                "full_name": raw_full_name,
                "department": department.pk,
                "designation": designation.pk,
                "status": status_code,
                "date_joined": date_joined_value,
                "employment_type": employment_type_code,
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