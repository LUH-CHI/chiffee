

Install
=======

To install copy the project into a djange workspace, then add the following line to the url matcher in urls.py:


    url(r'^', include('chiffee.urls', namespace="chiffee")),
    
also add the following to the settings file:

EMAIL_HOST = 'mailgate.uni-hannover.de'
LOGIN_REDIRECT_URL = 'chiffee:home'

and in there add the following to INSTALLED_APPS

    'chiffee',

