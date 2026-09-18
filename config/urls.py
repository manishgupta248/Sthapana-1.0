from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.accounts.urls')),
    path('', include('apps.core.urls')),
    path("people/", include("apps.people.urls")),
    path("tasks/", include("apps.tasks.urls")),
    path("telegram/", include("apps.telegram_bot.urls")),
    path("records/", include("apps.records.urls")),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
