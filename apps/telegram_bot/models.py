from django.conf import settings
from django.db import models


class TelegramUser(models.Model):
    """Maps a Telegram chat to a Sthapana system user.

    Only chat IDs listed here can talk to the bot (Decision #8 —
    whitelisted chat IDs only). Today this will hold a single row
    (your chat), but nothing about this table needs to change to add
    a second person later.
    """
    chat_id = models.CharField(max_length=32, unique=True, help_text="Telegram numeric Chat ID.")
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="telegram_profile"
    )
    is_active = models.BooleanField(
        default=True, help_text="Uncheck to block bot access without deleting the record."
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} ({self.chat_id})"


class BotState(models.Model):
    """A single row remembering the last Telegram message we've already
    processed, so restarting the bot doesn't reprocess old messages."""
    last_update_id = models.BigIntegerField(default=0)

    class Meta:
        verbose_name = "Bot State"
        verbose_name_plural = "Bot State"

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return f"Last processed update ID: {self.last_update_id}"