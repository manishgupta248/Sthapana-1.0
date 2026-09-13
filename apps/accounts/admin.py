from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

# We register our custom User using Django's own UserAdmin as a base,
# so we keep all its normal features (group management, permissions,
# password change form) without having to rebuild them ourselves.
admin.site.register(User, UserAdmin)