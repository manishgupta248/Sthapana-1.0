"""Ties an incoming Telegram message to the command registry, and
enforces the chat-ID whitelist. Never lets one bad message crash the
polling loop — errors are caught and logged, with a friendly reply."""

import logging

from .commands import COMMAND_REGISTRY
from .models import TelegramUser
from .services import TelegramClient

logger = logging.getLogger(__name__)


def _resolve_authorized_user(chat_id):
    try:
        mapping = TelegramUser.objects.select_related("user").get(
            chat_id=str(chat_id), is_active=True
        )
        return mapping.user
    except TelegramUser.DoesNotExist:
        return None


def handle_update(update, client: TelegramClient):
    message = update.get("message")
    if not message or "text" not in message:
        return  # ignore anything that isn't a plain text message for now

    chat_id = message["chat"]["id"]
    text = message["text"].strip()

    user = _resolve_authorized_user(chat_id)
    if user is None:
        logger.warning("Ignored message from unrecognised chat_id=%s", chat_id)
        return  # stay silent — don't confirm to a stranger that the bot exists

    if not text.startswith("/"):
        client.send_message(chat_id, "Sorry, I only understand commands starting with /. Try /help.")
        return

    command_word, _, args = text[1:].partition(" ")
    handler = COMMAND_REGISTRY.get(command_word.lower())

    if handler is None:
        client.send_message(chat_id, f"❓ Unknown command: /{command_word}\nType /help for the list.")
        return

    try:
        reply = handler(user, args.strip())
    except Exception:
        logger.exception("Command '/%s' raised an error", command_word)
        reply = "⚠️ Something went wrong running that. It's been logged."

    if reply:
        client.send_message(chat_id, reply)