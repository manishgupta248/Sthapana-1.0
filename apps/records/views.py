from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import redirect, render, get_object_or_404
from .forms import DocumentUploadForm, DocumentEditForm
from .models import Document, Tag, DocumentCategory
from .utils import resolve_tags
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import FileResponse, Http404
import os


@login_required
@permission_required("records.add_document", raise_exception=True)
def document_upload(request):
    similar_documents = None

    if request.method == "POST":
        form = DocumentUploadForm(request.POST, request.FILES)
        confirm_duplicate = request.POST.get("confirm_duplicate") == "true"

        if form.is_valid():
            title = form.cleaned_data["title"]
            similar_documents = Document.objects.filter(is_deleted=False, title__icontains=title)

            if similar_documents.exists() and not confirm_duplicate:
                return render(
                    request,
                    "records/document_upload.html",
                    {
                        "form": form,
                        "similar_documents": similar_documents[:5],
                        "show_duplicate_warning": True,
                        "MAX_DOCUMENT_UPLOAD_MB": settings.MAX_DOCUMENT_UPLOAD_MB,
                    },
                )

            document = form.save(commit=False)
            document.uploaded_by = request.user
            document.save()
            document.tags.set(resolve_tags(Tag, form.cleaned_data.get("tags", "")))

            stored_name = document.file.name.split("/")[-1]
            messages.success(
                request,
                f"Document '{document.title}' uploaded and filed under "
                f"{document.category.name} as {stored_name}.",
            )
            # Temporary redirect target — Steps 2.3/2.4 add a proper
            # detail page; for now this opens the Django admin record.
            return redirect("records:document_list")
    else:
        form = DocumentUploadForm()

    return render(
        request,
        "records/document_upload.html",
        {"form": form, "MAX_DOCUMENT_UPLOAD_MB": settings.MAX_DOCUMENT_UPLOAD_MB},
    )

SORTABLE_FIELDS = {
    "title": "title",
    "category": "category__name",
    "date": "document_date",
    "uploaded": "uploaded_at",
}


@login_required
@permission_required("records.view_document", raise_exception=True)
def document_list(request):
    documents = Document.objects.filter(is_deleted=False).select_related("category").prefetch_related("tags")

    query = request.GET.get("q", "").strip()
    if query:
        documents = documents.filter(
            Q(title__icontains=query) | Q(description__icontains=query) | Q(original_filename__icontains=query)
        )

    category_id = request.GET.get("category", "").strip()
    if category_id:
        documents = documents.filter(category_id=category_id)

    tag_id = request.GET.get("tag", "").strip()
    if tag_id:
        documents = documents.filter(tags__id=tag_id)

    date_from = request.GET.get("date_from", "").strip()
    if date_from:
        documents = documents.filter(document_date__gte=date_from)

    date_to = request.GET.get("date_to", "").strip()
    if date_to:
        documents = documents.filter(document_date__lte=date_to)

    sort = request.GET.get("sort", "date")
    direction = request.GET.get("dir", "desc")
    sort_field = SORTABLE_FIELDS.get(sort, "document_date")
    if direction == "desc":
        sort_field = f"-{sort_field}"
    documents = documents.order_by(sort_field).distinct()

    paginator = Paginator(documents, 25)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(
        request,
        "records/document_list.html",
        {
            "page_obj": page_obj,
            "categories": DocumentCategory.objects.filter(is_active=True),
            "tags": Tag.objects.all(),
            "query": query,
            "selected_category": category_id,
            "selected_tag": tag_id,
            "date_from": date_from,
            "date_to": date_to,
            "sort": sort,
            "direction": direction,
        },
    )

@login_required
@permission_required("records.view_document", raise_exception=True)
def document_detail(request, pk):
    document = get_object_or_404(Document, pk=pk, is_deleted=False)
    previewable = document.file_type in ["pdf", "png", "jpg", "jpeg"]
    return render(request, "records/document_detail.html", {"document": document, "previewable": previewable})


@login_required
@permission_required("records.view_document", raise_exception=True)
def document_download(request, pk):
    document = get_object_or_404(Document, pk=pk, is_deleted=False)
    if not document.file or not os.path.exists(document.file.path):
        raise Http404("File not found on disk.")
    return FileResponse(
        open(document.file.path, "rb"), as_attachment=False, filename=document.original_filename
    )


@login_required
@permission_required("records.change_document", raise_exception=True)
def document_edit(request, pk):
    document = get_object_or_404(Document, pk=pk, is_deleted=False)
    if request.method == "POST":
        form = DocumentEditForm(request.POST, instance=document)
        if form.is_valid():
            document = form.save()
            document.tags.set(resolve_tags(Tag, form.cleaned_data.get("tags", "")))
            messages.success(request, f"Document '{document.title}' updated.")
            return redirect("records:document_detail", pk=document.pk)
    else:
        form = DocumentEditForm(instance=document)
    return render(request, "records/document_form.html", {"form": form, "document": document, "title": "Edit Document"})


@login_required
@permission_required("records.delete_document", raise_exception=True)
def document_delete(request, pk):
    document = get_object_or_404(Document, pk=pk, is_deleted=False)
    if request.method == "POST":
        title = document.title
        document.soft_delete(request.user)
        messages.success(request, f"Document '{title}' moved to trash.")
        return redirect("records:document_list")
    return render(request, "records/document_confirm_delete.html", {"document": document})