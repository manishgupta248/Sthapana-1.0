from django import forms

from .models import Department, Designation, Employee
from .models import ContactDetails


class EmployeeForm(forms.ModelForm):
    """Used by both the web 'Add/Edit Employee' pages AND the Excel
    importer below — so a duplicate Employee ID, missing field, etc. is
    rejected the same way no matter which channel was used."""

    class Meta:
        model = Employee
        fields = [
            "employee_id",
            "full_name",
            "department",
            "designation",
            "status",
            "date_joined",
            "employment_type",
        ]
        widgets = {
            "date_joined": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            existing = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = (existing + " form-control").strip()
        # Only offer active departments/designations for new choices, but
        # still show the current one even if it was later deactivated.
        self.fields["department"].queryset = (
            Department.objects.filter(is_active=True)
            | Department.objects.filter(pk=self.instance.department_id)
        )
        self.fields["designation"].queryset = (
            Designation.objects.filter(is_active=True)
            | Designation.objects.filter(pk=self.instance.designation_id)
        )


class ExcelImportForm(forms.Form):
    excel_file = forms.FileField(
        label="Excel file (.xlsx)",
        widget=forms.ClearableFileInput(attrs={"class": "form-control", "accept": ".xlsx"}),
    )

# =======================================================

class ContactDetailsForm(forms.ModelForm):
    class Meta:
        model = ContactDetails
        exclude = ["employee", "created_at", "updated_at"]
        widgets = {
            "current_address": forms.Textarea(attrs={"rows": 3}),
            "permanent_address": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            existing = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = (existing + " form-control").strip()


class ContactImportForm(forms.Form):
    excel_file = forms.FileField(
        label="Excel file (.xlsx)",
        widget=forms.ClearableFileInput(attrs={"class": "form-control", "accept": ".xlsx"}),
    )