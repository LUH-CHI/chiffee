import logging

import ldap
from django.conf import settings
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand
from django_auth_ldap.backend import LDAPBackend

from chiffee.models import User

logger = logging.getLogger('syncldap')


# This command synchronizes local database with the LDAP server.
# New LDAP user -> new user in the local database.
# Deleted LDAP user -> local user is set to inactive.
class Command(BaseCommand):
    help = 'Syncing local users with LDAP... '

    def handle(self, *args, **options):
        self.populate_db()
        self.find_inactive_user()

    # Find all users in LDAP and add them to the database if needed.
    def populate_db(self):
        connection = ldap.initialize(settings.AUTH_LDAP_SERVER_URI)
        connection.simple_bind_s(settings.AUTH_LDAP_BIND_DN,
                                 settings.AUTH_LDAP_BIND_PASSWORD)
        filter_ = '(&(uid=*))'  # Customize this if necessary.
        ldap_users = connection.search_s(settings.BASE_DN,
                                         ldap.SCOPE_SUBTREE,
                                         filter_)
        connection.unbind()

        for ldap_user in ldap_users:
            username = ldap_user[1]['uid'][0].decode('UTF-8')
            if not User.objects.filter(username=username).exists():
                logger.info('Adding new user %s...' % username)

            user = LDAPBackend().populate_user(
                ldap_user[1]['uid'][0].decode('UTF-8'))
            user.is_active = True

            # Add a single group to the user.
            # When group information is not stored as part of the user info,
            # code needs to be modified.
            try:
                groups = ldap_user[1]['group']
            except KeyError:
                logger.info(
                    'User could not be added to a group and won\'t be able to '
                    'purchase anything.')
                continue

            groups = [g.decode('UTF-8') for g in groups]
            self.add_user_to_group(user, groups)
            user.save()

    # A user should belong to only one group.
    # Group priority: professors > employees > students
    def add_user_to_group(self, user, groups):
        if 'professors' in groups:
            group_name = 'professors'
        elif 'employees' in groups:
            group_name = 'employees'
        else:
            group_name = 'students'

        group = Group.objects.get(name=group_name)
        if len(user.groups.all()) == 0:
            group.user_set.add(user)
        else:
            user.groups.clear()
            group.user_set.add(user)

    # Mark all users with no LDAP entry inactive.
    def find_inactive_user(self):
        for user in User.objects.filter(is_active=True):
            ldap_user = LDAPBackend().populate_user(user.username)
            if ldap_user is None and not user.is_superuser:
                logger.info('User %s set to inactive.' % user)
                user.is_active = False
            user.save()
