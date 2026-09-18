"""Small, isolated helper functions for the records app — filename
generation and tag resolution, kept separate from models.py so they're
easy to find and reuse from both the upload view (Step 2.2) and any
future bulk-import tool."""

from pathlib import Path

from django.utils.text import slugify


def generate_document_filename(document, original_filename):
    """Builds the standard stored filename:
    {document date}_{slugified title}_{DOCnnnnn}.{original extension}

    Requires document.pk to already exist (i.e. call this AFTER the
    Document row has been saved once), since the ID is part of the name.
    """
    ext = Path(original_filename).suffix.lower()
    slug = slugify(document.title)[:60] or "document"
    date_str = document.document_date.isoformat()
    return f"{date_str}_{slug}_DOC{document.pk:05d}{ext}"


def resolve_tags(tag_model, raw_tag_string):
    """Turns a comma-separated string like 'budget, 2026, confidential'
    into a list of Tag instances, reusing existing tags case-insensitively
    and creating new ones only when genuinely new."""
    names = [t.strip() for t in raw_tag_string.split(",") if t.strip()]
    tags = []
    seen_lower = set()
    for name in names:
        lower = name.lower()
        if lower in seen_lower:
            continue
        seen_lower.add(lower)
        existing = tag_model.objects.filter(name__iexact=name).first()
        tags.append(existing or tag_model.objects.create(name=name))
    return tags