"""Shared logic for building a reminder summary — used by both the
scheduled automatic reminder (send_task_reminders command) and the
manual /remind bot command, so there's exactly one definition of what
counts as reminder-worthy."""

from html import escape as escape_html

from django.utils import timezone

from apps.tasks.models import Task


def build_reminder_summary(user):
    """Returns an HTML-formatted reminder message, or None if the user
    has no overdue or due-today tasks (i.e. nothing worth sending)."""
    today = timezone.localdate()
    tasks = (
        Task.objects.filter(assignee=user)
        .exclude(status__in=[Task.STATUS_COMPLETED, Task.STATUS_CANCELLED])
        .order_by("due_date")
    )
    overdue = [t for t in tasks if t.due_date < today]
    due_today = [t for t in tasks if t.due_date == today]

    if not overdue and not due_today:
        return None

    lines = ["⏰ <b>Task Reminder</b>", ""]
    if overdue:
        lines.append(f"⚠️ <b>Overdue ({len(overdue)})</b>")
        for task in overdue:
            lines.append(f"#{task.pk} — {escape_html(task.title)} (was due {task.due_date})")
        lines.append("")
    if due_today:
        lines.append(f"📅 <b>Due Today ({len(due_today)})</b>")
        for task in due_today:
            lines.append(f"#{task.pk} — {escape_html(task.title)}")

    return "\n".join(lines)