from contextlib import contextmanager
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Group, Permission
from django.core.exceptions import ObjectDoesNotExist
from django.utils import importlib


class GroupPermissions(object):

    def __init__(self, verbose=False):
        self.verbose = verbose
        self.grouplist = None

    def log(self, s):
        if self.verbose:
            print s

    @contextmanager
    def groups(self, *grouplist):
        """
        Enter a context block with a group or list of groups to set
        permissions for.

        if group is not a Group object then it will be treated
        as the name of a group and we try to get it or create it
        if necessary.
        """
        self.log("Permissions for:")
        self.grouplist = []
        for group in grouplist:
            assert isinstance(group, Group) or isinstance(group, basestring)
            if not isinstance(group, Group):
                (group, _) = Group.objects.get_or_create(name=group)
            self.grouplist.append(group)
            self.log("     - Group: {0}".format(group))
        yield
        self.grouplist = None

    def add_permissions(self, model_class, *permission_codenames):
        """
        Sets up group permissions for the groups defined in the current
        block context.

        model class should be a real model class, to avoid ambiguity.

        the other args are permission code names for the given model
        (we hope)
        """
        assert self.grouplist

        content_type = ContentType.objects.get_for_model(model_class)
        for permission_codename in permission_codenames:
            self.log(" -  {0}.{1}".format(
                model_class.__name__,
                permission_codename))
            try:
                perm = Permission.objects.get(
                    content_type=content_type,
                    codename=permission_codename)
            except ObjectDoesNotExist as e:
                raise ObjectDoesNotExist(
                    "{0} {content_type}.'{codename}'".format(
                        str(e),
                        content_type=content_type.model_class(),
                        codename=permission_codename))

            for group in self.grouplist:
                group.permissions.add(perm)

    def delete_all_group_permissions(self):
        self.log("Deleting ALL group permissions.")
        for group in Group.objects.all():
            group.permissions.clear()

    def create_custom_permissions(self, custom_permissions):
        self.log("Custom permissions")
        for (codename, name, model_class) in custom_permissions:
            self.log(' - {0}.{1}'.format(model_class.__name__, codename))
            Permission.objects.get_or_create(
                name=name,
                content_type=ContentType.objects.get_for_model(model_class),
                codename=codename)

    @classmethod
    def get_perm(cls, permission_name):
        """
        Return a permission object based on the custom permissions defined here
        """
        [(codename, model)] = [(c, m) for (c, _, m)
                               in cls.custom_permissions
                               if c == permission_name]
        content_type = ContentType.objects.get_for_model(model)
        return Permission.objects.get(codename=codename,
                                      content_type=content_type)

    @classmethod
    def has_perm(cls, user, permission):
        """
        Convenience method for testing if a user has our custom permissions.
        """
        return user.has_perm(cls.perm_name(permission))

    @classmethod
    def perm_name(cls, permission):
        """
        Retuns the name of one of our custom permissions in a useful
        <app>.<perm> format for using with user.has_perm, etc.
        """
        p = cls.get_perm(permission) \
            if isinstance(permission, basestring) else permission
        return "{0}.{1}".format(p.content_type.app_label, p.codename)

    #================================================================
    # Custom Permissions
    #================================================================
    '''
    Defined here and not in class Meta because South doesn't handle
    that yet and we would need to run syncdb --all on deployment.
    '''
    custom_permissions = [
        # (codename,     name,      model(for content_type))
    ]

    #================================================================
    # Group permissions
    #================================================================
    # Example:
    # group_permissions = {'readers': ((USER_MODEL, 'can_read'),)}

    def setup_groups_and_permissions(self):
        # Start with a clean slate
        self.delete_all_group_permissions()

        # Add all the permissions
        for app_name in settings.INSTALLED_APPS:
            try:
                module = importlib.import_module("%s.permissions" % app_name)
            except ImportError:
                continue
            perms = module.Permissions

            self.custom_permissions.append(perms.custom_permissions)
            self.create_custom_permissions(perms.custom_permissions)

            for group_name in perms.group_permissions:
                group_perms = perms.group_permissions[group_name]
                with self.groups(group_name):
                    for model, perm in group_perms:
                        self.add_permissions(model, perm)
