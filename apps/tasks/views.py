from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import TaskAttachmentFormSet, TaskForm
from .models import Task


@login_required
def task_list(request):
    tasks = Task.objects.select_related("assignee").all()
    status = request.GET.get("status", "").strip()
    if status:
        tasks = tasks.filter(status=status)
    return render(
        request,
        "tasks/task_list.html",
        {"tasks": tasks, "status_choices": Task.STATUS_CHOICES, "selected_status": status},
    )


@login_required
def my_tasks(request):
    """The in-app 'reminder' view: the logged-in user's own open/in-progress
    tasks, with overdue ones flagged."""
    tasks = (
        Task.objects.filter(assignee=request.user)
        .exclude(status__in=[Task.STATUS_COMPLETED, Task.STATUS_CANCELLED])
        .order_by("due_date")
    )
    return render(request, "tasks/my_tasks.html", {"tasks": tasks})


@login_required
def task_detail(request, pk):
    task = get_object_or_404(Task.objects.select_related("assignee", "created_by"), pk=pk)
    return render(request, "tasks/task_detail.html", {"task": task})


@login_required
@permission_required("tasks.add_task", raise_exception=True)
def task_add(request):
    if request.method == "POST":
        form = TaskForm(request.POST)
        formset = TaskAttachmentFormSet(request.POST, request.FILES)
        if form.is_valid() and formset.is_valid():
            task = form.save(commit=False)
            task.created_by = request.user
            task.save()
            formset.instance = task
            attachments = formset.save(commit=False)
            for attachment in attachments:
                attachment.task = task
                attachment.uploaded_by = request.user
                attachment.save()
            for obj in formset.deleted_objects:
                obj.delete()
            messages.success(request, f"Task '{task.title}' was added.")
            return redirect("tasks:task_detail", pk=task.pk)
    else:
        form = TaskForm()
        formset = TaskAttachmentFormSet()
    return render(request, "tasks/task_form.html", {"form": form, "formset": formset, "title": "Add Task"})


@login_required
@permission_required("tasks.change_task", raise_exception=True)
def task_edit(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.method == "POST":
        form = TaskForm(request.POST, instance=task)
        formset = TaskAttachmentFormSet(request.POST, request.FILES, instance=task)
        if form.is_valid() and formset.is_valid():
            form.save()
            attachments = formset.save(commit=False)
            for attachment in attachments:
                attachment.task = task
                attachment.uploaded_by = request.user
                attachment.save()
            for obj in formset.deleted_objects:
                obj.delete()
            messages.success(request, f"Task '{task.title}' was updated.")
            return redirect("tasks:task_detail", pk=task.pk)
    else:
        form = TaskForm(instance=task)
        formset = TaskAttachmentFormSet(instance=task)
    return render(request, "tasks/task_form.html", {"form": form, "formset": formset, "title": "Edit Task"})


@login_required
@permission_required("tasks.delete_task", raise_exception=True)
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.method == "POST":
        title = task.title
        task.delete()
        messages.success(request, f"Task '{title}' was permanently deleted.")
        return redirect("tasks:task_list")
    return render(request, "tasks/task_confirm_delete.html", {"task": task})