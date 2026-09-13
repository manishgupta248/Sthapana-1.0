from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import User


class StyledFormMixin:
    """
    Adds Bootstrap's 'form-control' styling class to every field
    automatically, so login/registration inputs look consistent
    without repetitive HTML.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


class StyledAuthenticationForm(StyledFormMixin, AuthenticationForm):
    pass


class RegistrationForm(StyledFormMixin, UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email')

    def save(self, commit=True):
        user = super().save(commit=False)
        # New accounts start inactive. Django's built-in login form
        # already refuses to log in inactive users automatically -
        # an Admin must activate the account from /admin/ first.
        user.is_active = False
        if commit:
            user.save()
        return user