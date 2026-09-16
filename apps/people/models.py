from django.core.validators import RegexValidator
from django.db import models
from simple_history.models import HistoricalRecords


class Department(models.Model):
    """A managed list of departments, so employee records always pick from
    the same fixed list instead of free-typed text (avoids typos and
    duplicate spellings like 'Comp Sci' vs 'Computer Science')."""

    name = models.CharField(max_length=150, unique=True)
    is_active = models.BooleanField(
        default=True,
        help_text="Uncheck to hide this department from new employee forms, "
        "without deleting past records that use it.",
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Designation(models.Model):
    """A managed list of designations/posts, same reasoning as Department."""

    name = models.CharField(max_length=150, unique=True)
    is_active = models.BooleanField(
        default=True,
        help_text="Uncheck to hide this designation from new employee forms, "
        "without deleting past records that use it.",
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Employee(models.Model):
    """The Core employee record — the small, stable set of fields needed
    on almost every screen. Detail tables (contact info, salary, etc.)
    will be added in later steps and will each link back to this record."""

    STATUS_CHOICES = [
        ("ACTIVE", "Active"),
        ("ON_LEAVE", "On Leave"),
        ("SUSPENDED", "Suspended"),
        ("RETIRED", "Retired"),
        ("RESIGNED", "Resigned"),
        ("DECEASED", "Deceased"),
        ("TRANSFERRED", "Transferred"),
    ]

    EMPLOYMENT_TYPE_CHOICES = [
        ("REGULAR", "Regular"),
        ("CONTRACT", "Contract"),
        ("HKRNL", "HKRNL"),
        ("DEPUTATION", "Deputation"),
        ("GUEST_FACULTY", "Guest Faculty"),
        ("OTHER", "Other"),
    ]

    INITIAL_CHOICES = [
        ("DR", "Dr."),
        ("MR", "Mr."),
        ("MRS", "Mrs."),
        ("MS", "Ms."),
        ("SHRI", "Shri"),
        ("SMT", "Smt."),
    ]

    EMPLOYEE_CATEGORY_CHOICES = [
        ("TEACHING", "Teaching"),
        ("WORKSHOP", "Workshop"),
        ("ADMINISTRATIVE", "Administrative"),
        ("OTHER", "Other"),
    ]


    initial = models.CharField(
        max_length=10, choices=INITIAL_CHOICES, blank=True, default="",
        help_text="Title/Salutation (optional).",
    )
    employee_id = models.CharField(
        max_length=20,
        unique=True,
        validators=[
            RegexValidator(
                r"^[A-Za-z0-9\-/]+$",
                "Employee ID can only contain letters, numbers, hyphens, and slashes.",
            )
        ],
        help_text="Your office's existing employee code. Must be unique.",
    )
    full_name = models.CharField(max_length=200)
    department = models.ForeignKey(
        Department, on_delete=models.PROTECT, related_name="employees"
    )
    designation = models.ForeignKey(
        Designation, on_delete=models.PROTECT, related_name="employees"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="ACTIVE")
    date_joined = models.DateField(
        blank=True, null=True,
        help_text="Optional for now — can be filled in later.",
    )
    employee_category = models.CharField(
        max_length=20, choices=EMPLOYEE_CATEGORY_CHOICES, default="OTHER",
        help_text="Broad category of role — separate from Employment Type.",
    )
    employment_type = models.CharField(
        max_length=20, choices=EMPLOYMENT_TYPE_CHOICES, default="REGULAR"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # This one line gives every Employee record a full change history —
    # who changed what, and when — automatically, with no extra code.
    history = HistoricalRecords()

    class Meta:
        ordering = ["full_name"]

    def __str__(self):
        return f"{self.employee_id} — {self.full_name}"

# ===============================================================

PHONE_VALIDATOR = RegexValidator(
    r"^[0-9+\-\s]{7,15}$",
    "Enter a valid phone number (digits, spaces, + and - only).",
)


class ContactDetails(models.Model):
    """How to reach an employee, and who to contact in an emergency.
    Linked one-to-one with Employee — each employee has exactly one of
    these, and editing it simply updates the current values (the audit
    trail from Step 1.1 still keeps every past version automatically)."""

    employee = models.OneToOneField(
        Employee, on_delete=models.CASCADE, related_name="contact_details"
    )
    personal_mobile = models.CharField(max_length=15, validators=[PHONE_VALIDATOR])
    alternate_mobile = models.CharField(
        max_length=15, validators=[PHONE_VALIDATOR], blank=True
    )
    personal_email = models.EmailField(blank=True)
    official_email = models.EmailField(blank=True)
    current_address = models.TextField()
    permanent_address = models.TextField()
    emergency_contact_name = models.CharField(max_length=150)
    emergency_contact_phone = models.CharField(max_length=15, validators=[PHONE_VALIDATOR])
    emergency_contact_relation = models.CharField(max_length=50)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    history = HistoricalRecords()

    def __str__(self):
        return f"Contact details for {self.employee.full_name}"