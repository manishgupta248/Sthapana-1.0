from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import redirect, render

from .forms import TelegramMessageForm
from .models import TelegramUser
from .services import TelegramAPIError, TelegramClient


@login_required
@user_passes_test(lambda u: u.is_staff)
def send_message(request):
    if request.method == "POST":
        form = TelegramMessageForm(request.POST)
        if form.is_valid():
            client = TelegramClient()
            text = form.cleaned_data["message"]
            sent, failed = 0, 0
            for mapping in TelegramUser.objects.filter(is_active=True):
                try:
                    client.send_message(mapping.chat_id, text)
                    sent += 1
                except TelegramAPIError:
                    failed += 1

            if sent:
                messages.success(request, f"Message sent to {sent} Telegram user(s).")
            if failed:
                messages.error(request, f"Failed to send to {failed} Telegram user(s).")
            return redirect("telegram_bot:send_message")
    else:
        form = TelegramMessageForm()

    return render(request, "telegram_bot/send_message.html", {"form": form})