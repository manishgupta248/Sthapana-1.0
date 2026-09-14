from django.db import migrations


def assign_permissions(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")

    def get_perm(codename):
        return Permission.objects.filter(
            content_type__app_label="people", codename=codename
        ).first()

    all_codenames = [
        "view_employee", "add_employee", "change_employee", "delete_employee",
        "view_department", "add_department", "change_department",
        "view_designation", "add_designation", "change_designation",
    ]
    perms = {name: get_perm(name) for name in all_codenames}

    group_permissions = {
        "ReadOnly": ["view_employee", "view_department", "view_designation"],
        "Clerk": ["view_employee", "add_employee", "change_employee"],
        "EstablishmentOfficer": [
            "view_employee", "add_employee", "change_employee",
            "view_department", "add_department", "change_department",
            "view_designation", "add_designation", "change_designation",
        ],
        "Admin": all_codenames,
    }

    for group_name, codenames in group_permissions.items():
        group = Group.objects.filter(name=group_name).first()
        if not group:
            continue
        for codename in codenames:
            perm = perms.get(codename)
            if perm:
                group.permissions.add(perm)


def reverse_noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("people", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(assign_permissions, reverse_noop),
    ]