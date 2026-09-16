from django.contrib import admin

from .models import BotState, TelegramUser


@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = ["user", "chat_id", "is_active", "created_at"]
    list_filter = ["is_active"]
    search_fields = ["chat_id", "user__username"]


@admin.register(BotState)
class BotStateAdmin(admin.ModelAdmin):
    list_display = ["last_update_id"]

    def has_add_permission(self, request):
        # Only one BotState row should ever exist.
        return not BotState.objects.exists()