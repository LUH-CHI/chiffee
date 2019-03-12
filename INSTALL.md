# Install

## Django
This project assumes, that you have Django installed. You can check
this using the command:
```bash
python -m django --version
```

If not, please follow the installation guide at
https://docs.djangoproject.com/en/2.0/intro/install/

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
