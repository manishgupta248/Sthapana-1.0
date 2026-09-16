"""Sends a reminder message to every active Telegram-linked user who
has overdue or due-today tasks. Meant to be run once a day by Windows
Task Scheduler — it does one pass and exits (no loop), so it's safe to
run whether or not the main bot (run_telegram_bot) is currently
running."""

from django.core.management.base import BaseCommand

from apps.telegram_bot.models import TelegramUser
from apps.telegram_bot.reminders import build_reminder_summary
from apps.telegram_bot.services import TelegramAPIError, TelegramClient


class Command(BaseCommand):
    help = "Send task reminders to all active Telegram users with overdue or due-today tasks."

    def handle(self, *args, **options):
        client = TelegramClient()
        sent, skipped, failed = 0, 0, 0

        for mapping in TelegramUser.objects.filter(is_active=True).select_related("user"):
            summary = build_reminder_summary(mapping.user)
            if summary is None:
                skipped += 1
                continue
            try:
                client.send_message(mapping.chat_id, summary)
                sent += 1
            except TelegramAPIError as exc:
                self.stderr.write(f"Failed to message chat_id={mapping.chat_id}: {exc}")
                failed += 1

        self.stdout.write(
            self.style.SUCCESS(f"Reminder run complete. Sent: {sent}, nothing-to-send: {skipped}, failed: {failed}.")
        )