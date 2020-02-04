# Installing

## Requirements

To run Chiffee, you will first need Python 3, pip, and Django installed on the server. To do so, run the following 
commands:
```
sudo apt-get install python3 python3-pip
pip3 install django
```

LDAP also requires some packages installed on the server. To do so, run the following command:
```
sudo apt-get install libsasl2-dev python-dev libldap2-dev libssl-dev
```

## Creating a Django project and virtual environment

To use Chiffee, we have to create a Django project first. This is done with the following command:
```
django-admin startproject mysite
```

This will create a `mysite` directory in your current directory.

Make sure to create a [virtual environment](https://docs.python.org/3/tutorial/venv.html) inside `mysite`, this will 
allow you to avoid any conflicts with existing system packages. We'll call the folder containing virtual environment 
`venv`:
```
virtualenv venv
```

## Cloning files from GitHub and installing required packages

Go into the newly created `mysite` directory and clone this repository:
```
git clone https://github.com/LUH-CHI/chiffee.git
```

Now activate your virtual environment with `source venv/bin/activate`, navigate to the cloned folder `chiffee` and 
install all packages listed [here](requirements.txt) by using the following command:
```
pip install -r requirements.txt
```

## Adding Chiffee URL's to your project

Now change the file `mysite/urls.py` by adding the following line to `urlpatterns`:
```
path('', include(('chiffee.urls', 'chiffee'), namespace='chiffee')),
```

This will add Chiffee URL's to your `mysite` project. The resulting `mysite/urls.py` will look like this (don't forget 
to add an import for `include`):
```
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(('chiffee.urls', 'chiffee'), namespace='chiffee')),
]

```

## Adding environment variables

It's a good practice to store important settings in a separate file instead of hard-coding them.

Create a file named `.env` and place it in the root `mysite` directory (where `manage.py` is). This file should look 
like this (don't leave an empty blank line at the end): 
```
LOGIN_REDIRECT_URL=chiffee:index
LOGIN_URL=chiffee:login
EMAIL_HOST=mailgate.uni-hannover.de
SECRET_KEY='kj8qe5q#g8e8ks^b@p@!z@3js%ndq@h=lu+jqr7l%#fo1ph8%$'
```

You should change `EMAIL_HOST` and `SECRET_KEY`, the latter can match any string of characters, ideally you should copy 
it from `mysite/settings.py`.

Users from the Leibniz Universität Hannover can leave `mailgate.uni-hannover.de` as their `EMAIL_HOST`.

You also want to import these environment variables when your project runs. Add the following line to 
`manage.py` inside the `main` function:
```
dotenv.load_dotenv()
```

It should look like this (don't forget the import):
```
import os
import sys

import dotenv


def main():
    dotenv.load_dotenv()

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()

```

If you're using WSGI, then you also have to modify your `mysite/wsgi.py`: 
```
import os

import dotenv

dotenv.load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()

```

## Changing settings.py

Add the following lines to `mysite/settings.py`:
```
LOGIN_REDIRECT_URL = os.getenv('LOGIN_REDIRECT_URL')
LOGIN_URL = os.getenv('LOGIN_URL')
EMAIL_HOST = os.getenv('EMAIL_HOST')
```

Also change the `SECRET_KEY` variable:
```
SECRET_KEY = os.getenv('SECRET_KEY')
```

Change `DEBUG` if running in production:
```
DEBUG = False
```

Add this variable right where `STATIC_URL` is:
```
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
```

Finally, extend the `INSTALLED_APPS` array with `chiffee` and `django_filters` like this:
```
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'chiffee',
    'django_filters',
]
```

Don't forget to modify `ALLOWED_HOSTS` to include your server address, for example:
```
ALLOWED_HOSTS = ['server.uni-hannover.de']
```

## Adding Bootstrap

Some servers might not be able to connect to the outer world and access Bootstrap online, for that purpose there's a 
static CSS file inside Chiffee, but you have to make it available for your project. Navigate to where your `manage.py` 
is and run the following command:
```
python manage.py collectstatic
```

Make sure to read [this section](https://docs.djangoproject.com/en/3.0/howto/deployment/wsgi/modwsgi/#serving-files) on 
how to serve static files on your server.

## Migrating

### 1.x to 2.0

If you're moving to v2.0, follow these steps:
  - Back up current database file `db.sqlite3` in case something goes wrong.
  - Follow installation instructions as if it was a new project.
  - Copy your database file to the project root directory.
  - Now we need to update the database to the new design, this is where Django migrations come in.
  - You need to copy all your old migrations into the new project first. To do this, copy the folder 
  `chiffee/migrations` into your new project placing it under the same location. If your old project has no migrations 
  for some reason, then generate them with `python manage.py makemigrations`.
  - Navigate to your (new) project folder, activate virtual environment and run `python manage.py migrate --fake` which 
  makes Django think that old migrations have already been applied to the database (which is sort of true).
  - Now run `python manage.py makemigrations --empty chiffee` which will generate an empty migrations file inside 
  `chiffee/migrations`.
  - Open this file and replace the `operations` array with the following:
  ```
  operations = [
      migrations.RenameModel('Buy', 'Purchase'),

      migrations.RenameField('Product', 'product_name', 'name'),
      migrations.RenameField('Product', 'product_price', 'price'),
      migrations.RenameField('Product', 'product_active', 'active'),
      migrations.AddField('Product',
                          'category',
                          models.IntegerField(choices=CATEGORIES,
                                              default=1)),

      migrations.RenameField('Purchase', 'buy_date', 'date'),
      migrations.RenameField('Purchase', 'buy_count', 'quantity'),
      migrations.RenameField('Purchase', 'buy_product', 'product'),
      migrations.RenameField('Purchase', 'buy_user', 'user'),
      migrations.RenameField('Purchase', 'buy_total', 'total_price'),
      migrations.RemoveField('Purchase', 'buy_address'),
      migrations.AddField('Purchase',
                          'key',
                          models.CharField(max_length=64,
                                           default=generate_key)),

      migrations.RenameField('Deposit', 'deposit_date', 'date'),
      migrations.RenameField('Deposit', 'deposit_value', 'amount'),
      migrations.RenameField('Deposit', 'deposit_user', 'user'),

      migrations.RenameField('Employee', 'allMails', 'get_all_emails'),

      migrations.RunSQL("UPDATE chiffee_product "
                        + "SET category = 2 "
                        + "WHERE product_categorie = 'F'"),
      migrations.RunSQL("UPDATE chiffee_product "
                        + "SET category = 3 "
                        + "WHERE product_categorie = 'I'"),

      migrations.RemoveField('Product', 'product_categorie'),

      migrations.RunSQL("UPDATE auth_group "
                        + "SET name = 'professors' "
                        + "WHERE name = 'prof'"),
      migrations.RunSQL("UPDATE auth_group "
                        + "SET name = 'employees' "
                        + "WHERE name = 'wimi'"),
      migrations.RunSQL("UPDATE auth_group "
                        + "SET name = 'students' "
                        + "WHERE name = 'stud'"),
  ]
  ```
  - Change imports at the top of the file to match this:
  ```
  from django.db import migrations, models

  from chiffee.models import CATEGORIES, generate_key
  ```
  - Now run `python manage.py migrate`, and if you followed the steps correctly, the new migration will be applied with 
  no issues.
  
## Installing from scratch

If you're doing a fresh installation, run the following commands:
```
python manage.py makemigrations
python manage.py migrate
```

# LDAP

You can use LDAP to authenticate your users. Skip this section if you're not planning to use it.

## Changing settings.py

Add the following lines to `mysite/settings.py` and fill out the blanks:
```
import ldap
from django_auth_ldap.config import GroupOfUniqueNamesType, LDAPSearch

# LDAP authentication
AUTH_LDAP_SERVER_URI = "" # Required.
PORT = 389
AUTH_LDAP_START_TLS = True # Make sure the certificate exists. "False" for testing only.
AUTH_LDAP_BIND_DN = "" # Optional.
AUTH_LDAP_BIND_PASSWORD = "" # Required when "AUTH_LDAP_BIND_DN" is used.
BASE_DN = 'dc=example,dc=com' # Modify user search.
AUTH_LDAP_USER_SEARCH = LDAPSearch(
    BASE_DN
    ldap.SCOPE_SUBTREE,
    '(uid=%(user)s)',
)

AUTH_LDAP_GROUP_SEARCH = LDAPSearch(
    'ou=group,dc=example,dc=com', # Modify group search.
    ldap.SCOPE_SUBTREE,
    '(objectClass=groupOfUniqueNames)',
)

# Modify mapping from LDAP entry to Django users.
# If user already exists, all values specified here will overwrite the existing ones.
AUTH_LDAP_USER_ATTR_MAP = {
    "username": "uid",
    "first_name": "",
    "last_name": "",
    "email": "",
}

AUTH_LDAP_GROUP_TYPE = GroupOfUniqueNamesType(name_attr='cn')
AUTH_LDAP_USER_FLAGS_BY_GROUP = {
    "is_superuser": "cn=,ou=,dc=example,dc=com", # Modify permission by group.
}

# Remove "ModelBackend" for LDAP authentication only.
# Remove "LDAPBackend" for Django authentication only.
# Order of entries is important if user exists in both backends.
# First entry is queried first, and LDAP overwrites existing user values!
AUTHENTICATION_BACKENDS = [
    'django_auth_ldap.backend.LDAPBackend',
    'django.contrib.auth.backends.ModelBackend',
]
```

## Synchronizing automatically

The django command `syncldap` can synchronize LDAP users with the local database. New users from LDAP are added, and 
deleted users are marked inactive.
Some customizations may be necessary in `mysite/chiffee/management/commands/syncldap.py`.

Either execute the command manually or use a cronjob to sync, e.g. every day at 11.59 pm.
```
crontab -e
59 23 * * * cd /home/user/chiffee/mysite && python3 manage.py syncldap
```

# Running

## Development

Use the following command to run a local development server:
```
python manage.py runserver
```

The output should look like this:
```
Performing system checks...

System check identified no issues (0 silenced).
February 20, 2018 - 16:24:58
Django version 1.11.4, using settings 'blub.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

## Production

The `runserver` command should only be used for development. Do not use it in production! 

If you want to use Django in production, there are several guides available. For example, 
[Apache](https://docs.djangoproject.com/en/3.0/howto/deployment/wsgi/modwsgi/).

Make sure to go through the official 
[Deployment checklist](https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/) as well.
