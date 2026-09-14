from django.urls import path

from . import views

app_name = "people"

urlpatterns = [
    path("", views.employee_list, name="employee_list"),
    path("add/", views.employee_add, name="employee_add"),
    path("import/", views.employee_import, name="employee_import"),
    path("<int:pk>/", views.employee_detail, name="employee_detail"),
    path("<int:pk>/edit/", views.employee_edit, name="employee_edit"),
    path("<int:pk>/delete/", views.employee_delete, name="employee_delete"),
]