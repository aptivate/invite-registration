# coding=utf-8
from __future__ import unicode_literals
import pytest
import mock

from django.conf import settings
from django.core import mail

from registration.views import SendActivationEmailView

from .factories import UserFactory


def generate_form_with_data(formclass, instance):
    form = formclass(instance=instance)
    available_fields = form.changed_data
    form_data = {}
    for field in available_fields:
        form_data[field] = getattr(instance, field)
    # Now instantiate form with data
    formwithdata = formclass(instance=instance, data=form_data)
    return formwithdata


@pytest.mark.integration
@pytest.mark.django_db
def test_new_contact_activation_email(rf):
    assert len(mail.outbox) == 0
    u = UserFactory()
    view = SendActivationEmailView()
    with mock.patch('registration.views.messages'):
        view.get(rf.get('/'), pk=u.id)
        assert len(mail.outbox) == 1
        email = mail.outbox[0]
        assert email.to[0] == u.business_email
        assert email.subject == 'Please activate your {0} account'.format(settings.SITE_NAME)
