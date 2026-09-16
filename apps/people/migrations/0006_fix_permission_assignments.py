from django.apps import apps as global_apps
from django.contrib.auth.management import create_permissions
from django.db import migrations


def assign_permissions(apps, schema_editor):
    # Force Django to create any Permission rows for this app that don't
    # exist yet. This normally happens automatically after every
    # migration finishes — but since we're assigning permissions from
    # within a migration itself, we need to trigger it early so the
    # permissions we want to hand out actually exist yet.
    app_config = global_apps.get_app_config("people")
    create_permissions(app_config, verbosity=0)

    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")

    def get_perm(codename):
        return Permission.objects.filter(
            content_type__app_label="people", codename=codename
        ).first()

    employee_codenames = [
        "view_employee", "add_employee", "change_employee", "delete_employee",
        "view_department", "add_department", "change_department",
        "view_designation", "add_designation", "change_designation",
    ]
    contact_codenames = [
        "view_contactdetails", "add_contactdetails",
        "change_contactdetails", "delete_contactdetails",
    ]

    group_permissions = {
        "ReadOnly": [
            "view_employee", "view_department", "view_designation", "view_contactdetails",
        ],
        "Clerk": [
            "view_employee", "add_employee", "change_employee",
            "view_contactdetails", "add_contactdetails", "change_contactdetails",
        ],
        "EstablishmentOfficer": [
            "view_employee", "add_employee", "change_employee",
            "view_department", "add_department", "change_department",
            "view_designation", "add_designation", "change_designation",
            "view_contactdetails", "add_contactdetails", "change_contactdetails",
        ],
        "Admin": employee_codenames + contact_codenames,
    }

    for group_name, codenames in group_permissions.items():
        group = Group.objects.filter(name=group_name).first()
        if not group:
            continue
        for codename in codenames:
            perm = get_perm(codename)
            if perm:
                group.permissions.add(perm)


def reverse_noop(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('people', '0005_remove_employee_initials_and_more'),
    ]

    operations = [
        migrations.RunPython(assign_permissions, reverse_noop),
    ]
