from django.urls import path

from . import views

app_name = "telegram_bot"

urlpatterns = [
    path("send/", views.send_message, name="send_message"),
]