"""Telegram command registry.

Each command is one small function. To add a new command later, write
a function shaped like:

    def cmd_something(user, args: str) -> str:
        ...
        return "reply text"

and register it with @command("something"). This registry is
deliberately flat and simple — the future Intent Router (Phase 10)
will sit in front of it, translating natural-language requests into
calls to these same functions, so this shape shouldn't need to change.

NOTE ON HTML ESCAPING: messages are sent with parse_mode="HTML", so
Telegram interprets < and > as real tags. Any text that comes from the
database (task titles, etc.) — not text we wrote ourselves — must be
passed through escape_html() before being inserted into a reply, or a
title containing '<' or '&' would break the whole message.
"""

from datetime import timedelta
from html import escape as escape_html

from django.utils import timezone
from apps.telegram_bot.reminders import build_reminder_summary
from apps.tasks.models import Task

COMMAND_REGISTRY = {}

STATUS_ALIASES = {
    "open": Task.STATUS_OPEN,
    "inprogress": Task.STATUS_IN_PROGRESS,
    "in-progress": Task.STATUS_IN_PROGRESS,
    "in_progress": Task.STATUS_IN_PROGRESS,
    "progress": Task.STATUS_IN_PROGRESS,
    "completed": Task.STATUS_COMPLETED,
    "complete": Task.STATUS_COMPLETED,
    "done": Task.STATUS_COMPLETED,
    "cancelled": Task.STATUS_CANCELLED,
    "canceled": Task.STATUS_CANCELLED,
}


def command(name):
    def decorator(func):
        COMMAND_REGISTRY[name] = func
        return func
    return decorator


@command("start")
def cmd_start(user, args):
    name = escape_html(user.get_full_name() or user.username)
    return f"👋 Welcome back, {name}!\n\nI'm the Sthapana bot. Type /help to see what I can do."


@command("help")
def cmd_help(user, args):
    lines = ["🤖 <b>Available commands</b>", ""]
    for name in sorted(COMMAND_REGISTRY):
        lines.append(f"/{name}")
    return "\n".join(lines)


@command("newtask")
def cmd_newtask(user, args):
    title = args.strip()
    if not title:
        return "⚠️ Usage: /newtask [title]\nExample: /newtask Meeting with Registrar"

    if not user.has_perm("tasks.add_task"):
        return "🚫 Your account doesn't have permission to create tasks."

    task = Task.objects.create(
        title=title,
        description="",
        assignee=user,
        due_date=timezone.localdate() + timedelta(days=1),
        status=Task.STATUS_OPEN,
        priority=Task.PRIORITY_HIGH,
        created_by=user,
    )
    safe_title = escape_html(task.title)
    assignee_name = escape_html(user.get_full_name() or user.username)
    return (
        f"✅ Task #{task.pk} created: <b>{safe_title}</b>\n"
        f"Due: {task.due_date} | Priority: High | Status: Open | Description: NA\n"
        f"(Assignee: {assignee_name})"
    )


@command("mytasks")
def cmd_mytasks(user, args):
    tasks = (
        Task.objects.filter(assignee=user)
        .exclude(status__in=[Task.STATUS_COMPLETED, Task.STATUS_CANCELLED])
        .order_by("due_date")
    )
    if not tasks:
        return "🎉 You have no open tasks."

    lines = ["📋 <b>Your open tasks</b>", ""]
    for task in tasks:
        flag = " ⚠️ OVERDUE" if task.is_overdue else ""
        safe_title = escape_html(task.title)
        lines.append(
            f"#{task.pk} — {safe_title}\n"
            f"   Due: {task.due_date}{flag} | {task.get_status_display()} | {task.get_priority_display()}"
        )
    lines.append("\nUse /setstatus [id] [status] to update one.")
    return "\n".join(lines)


@command("setstatus")
def cmd_setstatus(user, args):
    parts = args.strip().split(maxsplit=1)
    if len(parts) != 2:
        return (
            "⚠️ Usage: /setstatus [task id] [status]\n"
            "Status options: open, inprogress, completed, cancelled\n"
            "Example: /setstatus 12 completed"
        )

    task_id_raw, status_raw = parts
    if not task_id_raw.isdigit():
        return "⚠️ Task ID must be a number. Use /mytasks to see IDs."

    new_status = STATUS_ALIASES.get(status_raw.lower())
    if new_status is None:
        return "⚠️ Unknown status. Options: open, inprogress, completed, cancelled"

    if not user.has_perm("tasks.change_task"):
        return "🚫 Your account doesn't have permission to update tasks."

    try:
        task = Task.objects.get(pk=int(task_id_raw))
    except Task.DoesNotExist:
        return f"❓ No task found with ID #{task_id_raw}."

    old_status = task.get_status_display()
    task.status = new_status
    task.save(update_fields=["status"])
    safe_title = escape_html(task.title)
    return f"✅ Task #{task.pk} '{safe_title}' updated: {old_status} → {task.get_status_display()}"

@command("remind")
def cmd_remind(user, args):
    summary = build_reminder_summary(user)
    return summary or "🎉 Nothing overdue or due today — you're all caught up."