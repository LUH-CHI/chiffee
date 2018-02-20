# Install

## Django
This project assumes, that you have Django installed. You can check
this using the command:
```
python -m django --version
```

If not, please follow the installation guide at
https://docs.djangoproject.com/en/2.0/intro/install/

## Development environment

### Create Project
We first have to create a project. This is done with the following command:
```
django-admin startproject mysite
```

This will create a **mysite** directory in your current directory. If
it didn't work, see [Problems running django-admin](https://docs.djangoproject.com/en/2.0/faq/troubleshooting/#troubleshooting-django-admin)

### Clone files
Change inside the newly createt `mysite` directory and clone this repository

```
cd mysite
git clone https://github.com/LUH-CHI/chiffee.git
```

### Change URLs
Now use your default editor to change the file `mysite/urls.py` and add
the following and change the import statement:
```
    url(r'^', include('chiffee.urls', namespace="chiffee")),
```

It should afterwards look something like this:
```
from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^', include('chiffee.urls', namespace="chiffee")),
]
```

### Change Settings
Add the following line to the file `mysite/settings.py`
```
LOGIN_REDIRECT_URL = 'chiffee:home'
```

Users from the Leibniz Universität Hannover can use the mailgate
server, others may have to change these settings to reflect their
implementation. Please have a look at the
[Django help](https://docs.djangoproject.com/en/2.0/ref/settings/#std:setting-EMAIL_HOST)
and change your settings accordingly.
```
EMAIL_HOST = 'mailgate.uni-hannover.de'
```

Finally extend the `INSTALLED_APPS` array with chiffee. It should
afterwards look somthing like this:
```
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
```
python manage.py migrate
python manage.py makemigrations chiffee
python manage.py sqlmigrate chiffee 0001
python manage.py migrate
```


### Testrun
Test if the server is running using
```
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
 
