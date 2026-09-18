from django.urls import path

from . import views

app_name = "records"

urlpatterns = [
    path("upload/", views.document_upload, name="document_upload"),
    path("", views.document_list, name="document_list"),
        path("<int:pk>/", views.document_detail, name="document_detail"),
    path("<int:pk>/download/", views.document_download, name="document_download"),
    path("<int:pk>/edit/", views.document_edit, name="document_edit"),
    path("<int:pk>/delete/", views.document_delete, name="document_delete"),
]