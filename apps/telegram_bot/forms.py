from django import forms


class TelegramMessageForm(forms.Form):
    message = forms.CharField(
        label="Message to send to Telegram",
        widget=forms.Textarea(attrs={"rows": 5, "class": "form-control", "maxlength": 4096}),
        max_length=4096,
        help_text="Sent immediately to all active Telegram-linked users.",
    )