from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
    Our own User model, starting identical to Django's built-in one.
    Login is by username (as decided). Extra fields can be added here
    later without the painful migration problem of switching away from
    Django's default User after the fact.
    """
    pass