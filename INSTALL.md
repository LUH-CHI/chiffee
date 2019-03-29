# Install

## Django
This project assumes, that you have Django installed. You can check
this using the command:
```bash
python -m django --version
```

If not, please follow the installation guide at
https://docs.djangoproject.com/en/2.0/intro/install/

## LDAP authentication
You can use LDAP to authenticate your users. You'll need the following packages:
```bash
pip3 install python-ldap django-auth-ldap
```
Further help: https://django-auth-ldap.readthedocs.io/en/latest/install.html

## Development environment

### Create Project
We first have to create a project. This is done with the following command:
```bash
django-admin startproject mysite
```

This will create a **mysite** directory in your current directory. If
it didn't work, see [Problems running django-admin](https://docs.djangoproject.com/en/2.0/faq/troubleshooting/#troubleshooting-django-admin)

### Clone files
Change inside the newly createt `mysite` directory and clone this repository

```bash
cd mysite
git clone https://github.com/LUH-CHI/chiffee.git
```

### Change URLs
Now use your default editor to change the file `mysite/urls.py` and add
the following and change the import statement:
```python
    path('', include(('chiffee.urls', 'chiffee'), namespace="chiffee")),
```

It should afterwards look something like this:
```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(('chiffee.urls', 'chiffee'), namespace="chiffee")),
]
```

### Change Settings
Add the following line to the file `mysite/settings.py`
```python
LOGIN_REDIRECT_URL = 'chiffee:home'
```

Users from the Leibniz Universität Hannover can use the mailgate
server, others may have to change these settings to reflect their
implementation. Please have a look at the
[Django help](https://docs.djangoproject.com/en/2.0/ref/settings/#std:setting-EMAIL_HOST)
and change your settings accordingly.
```python
EMAIL_HOST = 'mailgate.uni-hannover.de'
```

Finally extend the `INSTALLED_APPS` array with chiffee. It should
afterwards look somthing like this:
```python
# Application definition

EMAIL_HOST = 'mailgate.uni-hannover.de'
LOGIN_REDIRECT_URL = 'chiffee:home'

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'chiffee',
]
```

#### Change Settings for LDAP
If you do not want to authenticate with LDAP, skip this.
Add the following lines to the file `mysite/settings.py` and change it to your needs.

```bash
import ldap
from django_auth_ldap.config import LDAPSearch, GroupOfUniqueNamesType

# LDAP Authentication
AUTH_LDAP_SERVER_URI = "" # required
PORT = 389
AUTH_LDAP_START_TLS = True # make sure cert exists; False for testing only
AUTH_LDAP_BIND_DN = "" # optional
AUTH_LDAP_BIND_PASSWORD = "" # required when BIND_DN is used
BASE_DN = 'dc=example,dc=com' # modify user search
AUTH_LDAP_USER_SEARCH = LDAPSearch(
    BASE_DN
    ldap.SCOPE_SUBTREE,
    '(uid=%(user)s)',
)

AUTH_LDAP_GROUP_SEARCH = LDAPSearch(
    'ou=group,dc=example,dc=com', # modify group search
    ldap.SCOPE_SUBTREE,
    '(objectClass=groupOfUniqueNames)',
)

# modify mapping from ldap entry to django users
# if user already exists, all values specified here will overwrite existing
AUTH_LDAP_USER_ATTR_MAP = {
    "username": "uid",
    "first_name": "",
    "last_name": "",
    "email": "",
}

AUTH_LDAP_GROUP_TYPE = GroupOfUniqueNamesType(name_attr='cn')
AUTH_LDAP_USER_FLAGS_BY_GROUP = {
    "is_superuser": "cn=,ou=,dc=example,dc=com", # modify permission by group
}

# remove ModelBackend for LDAP authentication only
# remove LDAPBackend for django authentication only
# order of entries important if user exists in both backends
# first entry queried first and LDAP overwrites existing user values!
AUTHENTICATION_BACKENDS = [
    'django_auth_ldap.backend.LDAPBackend',
    'django.contrib.auth.backends.ModelBackend',
]
```

#### Automatic LDAP Synchronization
You may need to customize some lines in 'mysite/chiffee/management/commands/syncldap.py'.
You can either manually synchronize with LDAP
```bash
python3 manage.py syncldap
```
Or use a cronjob to sync e.g. every day at 23.59.
```bash
crontab -e
59 23 * * * cd /home/user/chiffee/mysite && python3 manage.py syncldap
```

### Make migrations
Run the following commands to initialize the models and the database:
```bash
python manage.py migrate
python manage.py makemigrations chiffee
python manage.py sqlmigrate chiffee 0001
python manage.py migrate
```

### Testrun
Test if the server is running using
```bash
python manage.py runserver
```
The Output should look like this:

```
Performing system checks...

System check identified no issues (0 silenced).
February 20, 2018 - 16:24:58
Django version 1.11.4, using settings 'blub.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

If you look at the website using a web-browser. It should display an
empty site. With the title and the time.

## Production Environment
The runserver method should just be used for testing environments. If
you want to use django in production. There are several guides
available to use the application with for example
[Apache](https://docs.djangoproject.com/en/2.0/howto/deployment/wsgi/modwsgi/).

Please also have a look first at the
[Checklist](https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/).

## Using the site

### Creating the first user
Before using the site, first a user has to be createt. This can be done
using:

```bash
python manage.py createsuperuser
```

After creating the superuser, all configurations can be done in the
admin panel under `/admin` or in the users home panels under `/home`

### Managing products

TODO

### Managing users

TODO

### Making a deposit

The superuser, or any other user with admin priviledges has the
possebility to make a deposit for every user. This can be done in the
home screen for a loged in superuser. Simple insert the amount and
select a user from the drop-down menu.
