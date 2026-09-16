from django.urls import path

from . import views

app_name = "people"

urlpatterns = [
    path("", views.employee_list, name="employee_list"),
    path("add/", views.employee_add, name="employee_add"),
    path("export/", views.employee_export, name="employee_export"),
    path("import/", views.employee_import, name="employee_import"),
    path("<int:pk>/", views.employee_detail, name="employee_detail"),
    path("<int:pk>/edit/", views.employee_edit, name="employee_edit"),
    path("<int:pk>/delete/", views.employee_delete, name="employee_delete"),
    path("<int:employee_id>/contact/edit/", views.contact_details_edit, name="contact_details_edit"),
    path("<int:employee_id>/contact/delete/", views.contact_details_delete, name="contact_details_delete"),
    path("contact/import/template/", views.contact_import_template, name="contact_import_template"),
    path("contact/import/", views.contact_import, name="contact_import"),
    
]