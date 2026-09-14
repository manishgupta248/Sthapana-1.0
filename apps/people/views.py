import openpyxl
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import EmployeeForm, ExcelImportForm
from .models import Department, Designation, Employee

from django.core.exceptions import PermissionDenied

from .forms import ContactDetailsForm, ContactImportForm
from .models import ContactDetails

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