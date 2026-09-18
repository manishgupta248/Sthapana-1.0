"""Custom storage pointing at DOCUMENT_STORE_ROOT (outside the project
folder — see DECISIONS.md). Files are never given a public URL; all
access goes through permission-checked views.

Filenames: a brand-new document doesn't have a database ID yet (the
standard {date}_{slug}_DOC00001.ext pattern needs one), so it's first
saved under a temporary unique name, then immediately renamed by
Document.save() once its ID exists — see models.py._finalize_filename.
"""

import uuid
from pathlib import Path

from django.conf import settings
from django.core.files.storage import FileSystemStorage

document_storage = FileSystemStorage(location=settings.DOCUMENT_STORE_ROOT)


def document_upload_path(instance, filename):
    if not instance.pk:
        ext = Path(filename).suffix.lower()
        temp_name = f"_incoming_{uuid.uuid4().hex}{ext}"
        return f"{instance.category.folder_name}/{temp_name}"
    from .utils import generate_document_filename
    return f"{instance.category.folder_name}/{generate_document_filename(instance, filename)}"