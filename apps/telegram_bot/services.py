"""Thin wrapper around Telegram's Bot HTTP API using plain `requests`
calls — no bot framework dependency, so this stays simple and stable."""

import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

TELEGRAM_API_URL = "https://api.telegram.org/bot{token}/{method}"


class TelegramAPIError(Exception):
    """Raised when Telegram's API returns an error, or the request fails."""


class TelegramClient:
    def __init__(self, token=None, request_timeout=35):
        self.token = token or settings.TELEGRAM_BOT_TOKEN
        # Must be a little longer than the long-poll 'timeout' we pass to
        # getUpdates below, or our own request would time out first.
        self.request_timeout = request_timeout

    def _url(self, method):
        return TELEGRAM_API_URL.format(token=self.token, method=method)

    def _call(self, method, **params):
        try:
            response = requests.post(self._url(method), json=params, timeout=self.request_timeout)
            data = response.json()
        except requests.RequestException as exc:
            logger.error("Telegram request failed (%s): %s", method, exc)
            raise TelegramAPIError(str(exc)) from exc

        if not data.get("ok"):
            logger.error("Telegram API error (%s): %s", method, data)
            raise TelegramAPIError(data.get("description", "Unknown Telegram error"))
        return data["result"]

    def get_updates(self, offset, timeout=30):
        """Wait up to `timeout` seconds for new messages, then return them."""
        return self._call("getUpdates", offset=offset, timeout=timeout)

    def send_message(self, chat_id, text, parse_mode="HTML"):
        return self._call("sendMessage", chat_id=chat_id, text=text, parse_mode=parse_mode)