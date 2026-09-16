"""Runs the Telegram bot until stopped.

Start:  python manage.py run_telegram_bot
Stop:   Ctrl+C — a signal handler sets a flag that's checked every few
        seconds (the polling wait is kept short specifically so Ctrl+C
        is noticed quickly), then the loop finishes its current step,
        sends a goodbye message, and exits. No dangling threads.
"""

import logging
import signal

from django.core.management.base import BaseCommand

from apps.telegram_bot.bot import handle_update
from apps.telegram_bot.models import BotState, TelegramUser
from apps.telegram_bot.services import TelegramAPIError, TelegramClient

logger = logging.getLogger(__name__)

# How long each getUpdates() call waits for a new message before giving
# up and looping again. Shorter = bot notices Ctrl+C sooner; longer =
# fewer, more efficient requests to Telegram. 5s is a good balance.
POLL_TIMEOUT_SECONDS = 5


class Command(BaseCommand):
    help = "Run the Telegram bot's polling loop until stopped with Ctrl+C."

    def handle(self, *args, **options):
        client = TelegramClient(request_timeout=POLL_TIMEOUT_SECONDS + 10)
        state = BotState.get_solo()

        self._stop_requested = False

        def _request_stop(signum, frame):
            self.stdout.write("\nStop signal received, shutting down...")
            self._stop_requested = True

        # Explicit handlers for both Ctrl+C (SIGINT) and a "please stop"
        # signal (SIGTERM), rather than relying on Python's default
        # KeyboardInterrupt behaviour, which can be delayed on Windows.
        signal.signal(signal.SIGINT, _request_stop)
        signal.signal(signal.SIGTERM, _request_stop)

        self.stdout.write(self.style.SUCCESS("Telegram bot started. Press Ctrl+C to stop."))
        self._broadcast(client, "🟢 Sthapana bot is now online.")

        while not self._stop_requested:
            try:
                updates = client.get_updates(offset=state.last_update_id + 1, timeout=POLL_TIMEOUT_SECONDS)
            except TelegramAPIError as exc:
                logger.error("Polling error, will retry: %s", exc)
                continue

            for update in updates:
                if self._stop_requested:
                    break
                handle_update(update, client)
                state.last_update_id = update["update_id"]
                state.save(update_fields=["last_update_id"])

        self._broadcast(client, "🔴 Sthapana bot is going offline. Goodbye for now!")
        self.stdout.write(self.style.SUCCESS("Telegram bot stopped cleanly."))

    def _broadcast(self, client, text):
        for mapping in TelegramUser.objects.filter(is_active=True):
            try:
                client.send_message(mapping.chat_id, text)
            except TelegramAPIError:
                logger.warning("Could not message chat_id=%s", mapping.chat_id)