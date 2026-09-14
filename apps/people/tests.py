from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse

from .forms import EmployeeForm
from .models import Department, Designation, Employee
from .models import ContactDetails

from io import BytesIO

import openpyxl
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()


class EmployeeModelTests(TestCase):
    def setUp(self):
        self.department = Department.objects.create(name="Computer Science")
        self.designation = Designation.objects.create(name="Assistant Professor")

    def test_employee_can_be_created_and_retrieved(self):
        Employee.objects.create(
            employee_id="EMP001", full_name="Test Employee",
            department=self.department, designation=self.designation,
            status="ACTIVE", date_joined="2020-01-01", employment_type="REGULAR",
        )
        retrieved = Employee.objects.get(employee_id="EMP001")
        self.assertEqual(retrieved.full_name, "Test Employee")

    def test_duplicate_employee_id_rejected_at_database_level(self):
        Employee.objects.create(
            employee_id="EMP002", full_name="First",
            department=self.department, designation=self.designation,
            status="ACTIVE", date_joined="2020-01-01", employment_type="REGULAR",
        )
        with self.assertRaises(Exception):
            Employee.objects.create(
                employee_id="EMP002", full_name="Second",
                department=self.department, designation=self.designation,
                status="ACTIVE", date_joined="2021-01-01", employment_type="REGULAR",
            )


class EmployeeFormValidationTests(TestCase):
    def setUp(self):
        self.department = Department.objects.create(name="Physics")
        self.designation = Designation.objects.create(name="Clerk")

    def test_duplicate_employee_id_rejected_via_form(self):
        Employee.objects.create(
            employee_id="EMP100", full_name="Existing Person",
            department=self.department, designation=self.designation,
            status="ACTIVE", date_joined="2020-01-01", employment_type="REGULAR",
        )
        form = EmployeeForm(data={
            "employee_id": "EMP100", "full_name": "New Person",
            "department": self.department.pk, "designation": self.designation.pk,
            "status": "ACTIVE", "date_joined": "2022-01-01", "employment_type": "REGULAR",
        })
        self.assertFalse(form.is_valid())
        self.assertIn("employee_id", form.errors)


class EmployeePermissionTests(TestCase):
    def setUp(self):
        self.department = Department.objects.create(name="Chemistry")
        self.designation = Designation.objects.create(name="Lab Assistant")
        self.employee = Employee.objects.create(
            employee_id="EMP200", full_name="Someone",
            department=self.department, designation=self.designation,
            status="ACTIVE", date_joined="2020-01-01", employment_type="REGULAR",
        )
        clerk_group, _ = Group.objects.get_or_create(name="Clerk")
        self.clerk_user = User.objects.create_user(username="clerk1", password="testpass123")
        self.clerk_user.groups.add(clerk_group)
        self.clerk_user.is_active = True
        self.clerk_user.save()

    def test_clerk_without_delete_permission_cannot_delete_employee(self):
        self.client.login(username="clerk1", password="testpass123")
        response = self.client.post(reverse("people:employee_delete", args=[self.employee.pk]))
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Employee.objects.filter(pk=self.employee.pk).exists())
class ContactDetailsTests(TestCase):
    def setUp(self):
        self.department = Department.objects.create(name="Mathematics")
        self.designation = Designation.objects.create(name="Professor")
        self.employee = Employee.objects.create(
            employee_id="EMP300", full_name="Contact Test Person",
            department=self.department, designation=self.designation,
            status="ACTIVE", date_joined="2020-01-01", employment_type="REGULAR",
        )

    def test_contact_details_can_be_created_for_employee(self):
        contact = ContactDetails.objects.create(
            employee=self.employee, personal_mobile="9876543210",
            current_address="123 Test Street", permanent_address="123 Test Street",
            emergency_contact_name="Test Contact", emergency_contact_phone="9123456780",
            emergency_contact_relation="Spouse",
        )
        self.assertEqual(self.employee.contact_details, contact)

    def test_employee_can_only_have_one_contact_details_record(self):
        ContactDetails.objects.create(
            employee=self.employee, personal_mobile="9876543210",
            current_address="Address A", permanent_address="Address A",
            emergency_contact_name="A", emergency_contact_phone="9111111111",
            emergency_contact_relation="Friend",
        )
        with self.assertRaises(Exception):
            ContactDetails.objects.create(
                employee=self.employee, personal_mobile="9999999999",
                current_address="Address B", permanent_address="Address B",
                emergency_contact_name="B", emergency_contact_phone="9222222222",
                emergency_contact_relation="Friend",
            )

class LookupExcelImportAdminTests(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(
            username="admin1", password="testpass123", email="admin1@example.com"
        )
        Department.objects.create(name="Existing Dept")

    def test_import_creates_new_department_and_skips_existing(self):
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.append(["Name", "Is Active"])
        sheet.append(["New Department", "Yes"])
        sheet.append(["Existing Dept", "Yes"])
        buffer = BytesIO()
        workbook.save(buffer)
        buffer.seek(0)

        uploaded_file = SimpleUploadedFile(
            "departments.xlsx", buffer.read(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

        self.client.login(username="admin1", password="testpass123")
        response = self.client.post(
            "/admin/people/department/import-excel/", {"excel_file": uploaded_file}
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Department.objects.filter(name="New Department").exists())
        self.assertEqual(Department.objects.filter(name__iexact="Existing Dept").count(), 1)
