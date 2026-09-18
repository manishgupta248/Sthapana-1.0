"""Assigns Document permissions to the existing role groups.

NOTE: this creates the Permission objects itself via get_or_create,
rather than assuming Django's auto-generated default permissions
already exist — this is deliberately more defensive than the earlier
Contact Details permission migration, which broke because it ran
before those permissions had been auto-created (see PROGRESS.md,
2026-09-16 entry). This version can't hit that bug."""

from django.db import migrations

PERMISSIONS = ["add_document", "change_document", "delete_document", "view_document"]

# Delete is Admin-only, matching the same rule already applied to
# Employee and Task (DECISIONS.md #24).
GROUP_PERMISSIONS = {
    "Admin": PERMISSIONS,
    "EstablishmentOfficer": ["add_document", "change_document", "view_document"],
    "Clerk": ["add_document", "change_document", "view_document"],
    "ReadOnly": ["view_document"],
}


def assign_permissions(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")
    ContentType = apps.get_model("contenttypes", "ContentType")
    Document = apps.get_model("records", "Document")

    content_type = ContentType.objects.get_for_model(Document)

    codename_to_permission = {}
    labels = {
        "add_document": "Can add document",
        "change_document": "Can change document",
        "delete_document": "Can delete document",
        "view_document": "Can view document",
    }
    for codename in PERMISSIONS:
        permission, _ = Permission.objects.get_or_create(
            codename=codename, content_type=content_type,
            defaults={"name": labels[codename]},
        )
        codename_to_permission[codename] = permission

    for group_name, codenames in GROUP_PERMISSIONS.items():
        try:
            group = Group.objects.get(name=group_name)
        except Group.DoesNotExist:
            continue
        for codename in codenames:
            group.permissions.add(codename_to_permission[codename])


def remove_permissions(apps, schema_editor):
    pass  # not reversed — safe no-op, matches Django's own convention for permission migrations


class Migration(migrations.Migration):
    dependencies = [("records", "0002_seed_categories")]
    operations = [migrations.RunPython(assign_permissions, remove_permissions)]