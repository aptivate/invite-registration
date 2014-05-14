from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.forms import (
    UserCreationForm, UserChangeForm, PasswordResetForm
)
from django.forms import ValidationError
from django.utils.http import int_to_base36
import mail
from .models import User


#######################################################################
# Admin contacts forms
#######################################################################
class AdminUserCreationForm(UserCreationForm):
    """
    A form that creates a user, with no privileges, from the given email and
    password.
    """

    def __init__(self, *args, **kargs):
        super(AdminUserCreationForm, self).__init__(*args, **kargs)
        del self.fields['username']

    class Meta:
        model = User
        fields = ("business_email",)


class AdminUserChangeForm(UserChangeForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """

    def __init__(self, *args, **kargs):
        super(UserChangeForm, self).__init__(*args, **kargs)
        del self.fields['username']

    class Meta:
        model = User


#######################################################################
# Password reset forms
#######################################################################
class ContactPasswordResetForm(PasswordResetForm):
    def clean_email(self):
        """
        Validates that an active user exists with the given email address.
        """
        UserModel = get_user_model()
        email = self.cleaned_data["email"]
        self.users_cache = UserModel._default_manager.filter(
            business_email__iexact=email)
        if not len(self.users_cache):
            raise ValidationError(self.error_messages['unknown'])
        if not any(user.is_active for user in self.users_cache):
            # none of the filtered users are active
            raise ValidationError(self.error_messages['unknown'])
        return email

    def save(self, subject,
             email_template_name='registration/password_reset_email.html',
             use_https=False, token_generator=default_token_generator,
             from_email=None, request=None):
        """
        Generates a one-use only link for resetting password and sends to the
        user.
        """
        for user in self.users_cache:
            ctx = {
                'email': user.business_email,
                'site': settings.SITE_HOSTNAME,
                'uid': int_to_base36(user.pk),
                'user': user,
                'token': token_generator.make_token(user),
                'protocol': use_https and 'https' or 'http',
            }
            options = {
                'subject': subject,
                'from_email': from_email,
                'to': [user.business_email],
                'template_name': email_template_name,
                'context': ctx
            }
            mail.notify(options)
