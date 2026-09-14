from django.db import migrations


def assign_permissions(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")

    def get_perm(codename):
        return Permission.objects.filter(
            content_type__app_label="people", codename=codename
        ).first()

    codenames = [
        "view_contactdetails", "add_contactdetails",
        "change_contactdetails", "delete_contactdetails",
    ]
    perms = {name: get_perm(name) for name in codenames}

    group_permissions = {
        "ReadOnly": ["view_contactdetails"],
        "Clerk": ["view_contactdetails", "add_contactdetails", "change_contactdetails"],
        "EstablishmentOfficer": [
            "view_contactdetails", "add_contactdetails", "change_contactdetails",
        ],
        "Admin": codenames,
    }

    for group_name, names in group_permissions.items():
        group = Group.objects.filter(name=group_name).first()
        if not group:
            continue
        for name in names:
            perm = perms.get(name)
            if perm:
                group.permissions.add(perm)


def reverse_noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("people", "0002_assign_group_permissions"),
    ]

    operations = [
        migrations.RunPython(assign_permissions, reverse_noop),
    ]