from django.db import migrations

CATEGORIES = [
    ("Notices and Circulars", "Notices_and_Circulars"),
    ("Booklets", "Booklets"),
    ("Financial Records", "Financial_Records"),
    ("Policy Documents", "Policy_Documents"),
    ("Miscellaneous", "Miscellaneous"),
]


def seed_categories(apps, schema_editor):
    DocumentCategory = apps.get_model("records", "DocumentCategory")
    for name, folder_name in CATEGORIES:
        DocumentCategory.objects.get_or_create(name=name, defaults={"folder_name": folder_name})


def remove_categories(apps, schema_editor):
    DocumentCategory = apps.get_model("records", "DocumentCategory")
    DocumentCategory.objects.filter(folder_name__in=[f for _, f in CATEGORIES]).delete()


class Migration(migrations.Migration):
    dependencies = [("records", "0001_initial")]
    operations = [migrations.RunPython(seed_categories, remove_categories)]