# coding=utf-8
from __future__ import unicode_literals
import factory
from django.contrib.auth.models import Group
from registration.models import User
from registration.group_permissions import GroupPermissions


class UserFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = User

    # must be unique so we specify and increase
    business_email = factory.Sequence(lambda n: "email%d@test.com" % n)
    first_name = factory.Sequence(lambda n: "ｆíｒѕｔ %d" % n)
    last_name = factory.Sequence(lambda n: "ｌåｓｔɭａｓｔ %d" % n)

    # Other required fields (you will still need to handle password
    # yourself depending on what you want to do
    gender = 'female'
    contact_type = 'ｃòлｔáｃｔ ｔｙｐé'
    title = 'ｔïｔｌë'
