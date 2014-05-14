invite-registration
===================

invite-registration is a Django app for managing users and their registration when you need to control creation of accounts, but it is up to users to activate them by creating passwords.

Users are added in Django's administration interface in the same way as with a built 'django.contrib.admin' app. The difference is that they can be then invited to activate their accounts (a new action on the action row of the change user page). If they are, then they will receive an activation email to their email address which also doubles as their log-in username. On page linked in the email they can then set password and with that activate their account.


WARNING
-------
This app has not been widely tested yet so proceed with caution.


Installation
------------
After you have added app's code somewhere where Python can find it, you need to do the following:

1. Add it to ``INSTALLED_APPS``
2. Add to ``settings.py``: ``AUTH_USER_MODEL = 'registration.User'``
3. Also set ``LOGIN_REDIRECT_URL``
4. Set ``EMAIL_BOT_ADDRESS`` (sender of emails), ``SITE_NAME`` (website's name) and ``SITE_HOSTNAME`` (domain where it is hosted including port number when it is not 80)
5. Make sure that ``TEMPLATE_CONTEXT_PROCESSORS`` also include ``messages`` processor
