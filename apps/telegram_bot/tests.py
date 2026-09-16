from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase
from django.utils import timezone

from apps.tasks.models import Task

from .bot import _resolve_authorized_user
from .commands import cmd_mytasks, cmd_newtask, cmd_setstatus
from .models import TelegramUser
from .reminders import build_reminder_summary

User = get_user_model()


class TelegramWhitelistTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="manish", password="testpass123")

    def test_known_chat_id_resolves_to_user(self):
        TelegramUser.objects.create(chat_id="12345", user=self.user, is_active=True)
        self.assertEqual(_resolve_authorized_user("12345"), self.user)

    def test_unknown_chat_id_resolves_to_none(self):
        self.assertIsNone(_resolve_authorized_user("99999"))

    def test_inactive_mapping_is_not_authorized(self):
        TelegramUser.objects.create(chat_id="12345", user=self.user, is_active=False)
        self.assertIsNone(_resolve_authorized_user("12345"))


class TelegramCommandTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="manish", password="testpass123")
        for codename in ["add_task", "change_task"]:
            perm = Permission.objects.get(codename=codename, content_type__app_label="tasks")
            self.user.user_permissions.add(perm)

    def test_newtask_creates_task_with_correct_defaults(self):
        reply = cmd_newtask(self.user, "Meeting with Registrar")
        task = Task.objects.get(title="Meeting with Registrar")
        self.assertEqual(task.assignee, self.user)
        self.assertEqual(task.status, Task.STATUS_OPEN)
        self.assertEqual(task.priority, Task.PRIORITY_HIGH)
        self.assertEqual(task.due_date, timezone.localdate() + timedelta(days=1))
        self.assertEqual(task.description, "")
        self.assertIn(f"#{task.pk}", reply)

    def test_newtask_without_title_returns_usage_message(self):
        reply = cmd_newtask(self.user, "")
        self.assertIn("Usage", reply)
        self.assertEqual(Task.objects.count(), 0)

    def test_newtask_without_permission_is_refused(self):
        no_perm_user = User.objects.create_user(username="clerk2", password="testpass123")
        reply = cmd_newtask(no_perm_user, "Some Task")
        self.assertIn("permission", reply)
        self.assertEqual(Task.objects.count(), 0)

    def test_newtask_escapes_html_in_title(self):
        reply = cmd_newtask(self.user, "Meeting <Registrar> & Staff")
        self.assertNotIn("<Registrar>", reply)
        self.assertIn("&lt;Registrar&gt;", reply)

    def test_mytasks_lists_only_open_tasks_for_that_user(self):
        Task.objects.create(
            title="Open Task", assignee=self.user, created_by=self.user,
            due_date=timezone.localdate(), status=Task.STATUS_OPEN,
        )
        Task.objects.create(
            title="Done Task", assignee=self.user, created_by=self.user,
            due_date=timezone.localdate(), status=Task.STATUS_COMPLETED,
        )
        reply = cmd_mytasks(self.user, "")
        self.assertIn("Open Task", reply)
        self.assertNotIn("Done Task", reply)

    def test_setstatus_updates_task(self):
        task = Task.objects.create(
            title="Some Task", assignee=self.user, created_by=self.user,
            due_date=timezone.localdate(), status=Task.STATUS_OPEN,
        )
        reply = cmd_setstatus(self.user, f"{task.pk} completed")
        task.refresh_from_db()
        self.assertEqual(task.status, Task.STATUS_COMPLETED)
        self.assertIn("Open", reply)
        self.assertIn("Completed", reply)

    def test_setstatus_unknown_task_id(self):
        reply = cmd_setstatus(self.user, "9999 completed")
        self.assertIn("No task found", reply)

    def test_setstatus_invalid_status_word(self):
        task = Task.objects.create(
            title="Some Task", assignee=self.user, created_by=self.user,
            due_date=timezone.localdate(), status=Task.STATUS_OPEN,
        )
        reply = cmd_setstatus(self.user, f"{task.pk} banana")
        self.assertIn("Unknown status", reply)
        task.refresh_from_db()
        self.assertEqual(task.status, Task.STATUS_OPEN)


class ReminderSummaryTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="manish", password="testpass123")

    def test_no_summary_when_nothing_due(self):
        Task.objects.create(
            title="Future Task", assignee=self.user, created_by=self.user,
            due_date=timezone.localdate() + timedelta(days=5), status=Task.STATUS_OPEN,
        )
        self.assertIsNone(build_reminder_summary(self.user))

    def test_summary_includes_overdue_and_due_today_separately(self):
        Task.objects.create(
            title="Overdue Task", assignee=self.user, created_by=self.user,
            due_date=timezone.localdate() - timedelta(days=2), status=Task.STATUS_OPEN,
        )
        Task.objects.create(
            title="Today Task", assignee=self.user, created_by=self.user,
            due_date=timezone.localdate(), status=Task.STATUS_OPEN,
        )
        summary = build_reminder_summary(self.user)
        self.assertIn("Overdue Task", summary)
        self.assertIn("Today Task", summary)
        self.assertIn("Overdue (1)", summary)
        self.assertIn("Due Today (1)", summary)

    def test_completed_tasks_excluded_from_summary(self):
        Task.objects.create(
            title="Done Task", assignee=self.user, created_by=self.user,
            due_date=timezone.localdate() - timedelta(days=2), status=Task.STATUS_COMPLETED,
        )
        self.assertIsNone(build_reminder_summary(self.user))