from django.core.management.base import BaseCommand, CommandError
from chiffee.models import User
from django.conf import settings
from django.contrib.auth.models import Group
from django_auth_ldap.backend import LDAPBackend
import logging
import ldap


logger = logging.getLogger('syncldap')


# This command syncronizes the LDAP server with the local database
# New LDAP user -> new entry for user in local database
# Deleted LDAP user -> existing user is set to inactive in local database
class Command(BaseCommand):
	help = 'Sync local database with LDAP.' + \
			' Mark users inactive and retrieve new user.'

	def handle(self, *args, **options):
		self.populate_db()
		self.find_inactive_user()

	# find all users in LDAP and add to database if missing
	def populate_db(self):
		con = ldap.initialize(settings.AUTH_LDAP_SERVER_URI)
		con.simple_bind_s(settings.AUTH_LDAP_BIND_DN, settings.AUTH_LDAP_BIND_PASSWORD)
		filter_ = '(&(uid=*))' # customize this if necessary
		ldap_user = con.search_s(settings.BASE_DN, ldap.SCOPE_SUBTREE, filter_)
		con.unbind()
		for u in ldap_user:
			username = u[1]['uid'][0].decode('UTF-8')
			if not User.objects.filter(username=username).exists():
				logger.info("Add new user '%s' from LDAP" % username)

			user = LDAPBackend().populate_user(u[1]['uid'][0].decode('UTF-8'))
			user.is_active = True

			# add a single group (wimi, stud, prof) to a user
			# has to be rewritten if group information is not stored per user
			# but instead each group in ldap stores its member!
			try:
				groups = u[1]['group'] # customize this
			except KeyError:
				logger.info("User could not be added to a group and won't be able to purchase anything.")
				continue

			groups = [g.decode('UTF-8') for g in groups]
			self.add_user_to_group(user, groups)
			user.save()

	# a user should only belong to one group
	# hardcoded hierachy prof > wimi > stud
	def add_user_to_group(self, user, groups):
		group_name = "stud"
		if "prof" in groups:
			group_name = "prof"
		elif "wimi" in groups:
			group_name = "wimi"

		group = Group.objects.get(name=group_name)
		if len(user.groups.all()) == 0:
			group.user_set.add(user)
		else:
			user.groups.clear()
			group.user_set.add(user)

	# mark all users with no LDAP entry inactive
	def find_inactive_user(self):
		for user in User.objects.filter(is_active=True):
			ldap_user = LDAPBackend().populate_user(user.username)
			if ldap_user is None and not user.is_superuser:
				logger.info("User '%s' was set to inactive." % user)
				user.is_active = False
				user.save()
