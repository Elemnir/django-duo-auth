=================
 Django-Duo-Auth
=================

A Django middleware that adds 2-factor authentication via Duo.

``django-duo-auth`` is designed to be easily integrated into an existing Django project to quickly add 2-factor authentication. It supports one or more Duo applications and uses the configured ``AUTHENTICATION_BACKENDS`` to select which users it should authenticate under which circumstance.

--------------
 Installation
--------------

``django-duo-auth`` can be installed from PyPI, and depends on ``duo-universal``.

::
    
    ?> pip install django-duo-auth

If you wish to use the traditional iframe-based prompt, install like this instead

::

    ?> pip install django-duo-auth[legacy]

---------------
 Configuration
---------------

To enable Duo authentication, first add the following to ``settings.py``::

    # Add duo_auth to the list of installed apps
    INSTALLED_APPS = [
        # ...
        'duo_auth',
    ]

    # The DuoAuthMiddleware requires and must come after the SessionMiddleware
    # and AuthenticationMiddleware
    MIDDLEWARE = [
        # ...
        'duo_auth.middleware.DuoAuthMiddleware',
    ]

    DUO_CONFIG = {
        'DEFAULT': {
            'API_HOSTNAME': '<api-host-url>',
            'CLIENT_ID': '<integration_key>',
            'CLIENT_SECRET': '<secret_key>',
            'FIRST_STAGE_BACKENDS': [
                'django.contrib.auth.backends.ModelBackend',
            ]
        }
    }

Then include the URLs in ``urls.py``::

    from django.urls import path, include

    urlpatterns = [
        # ...
        path('duo/',  include('duo_auth.urls')),
    ]

And that's it! 

By default, the Duo Universal Prompt will be used. If the traditional iframe-based prompt is desired, add ``DUO_LEGACY_PROMPT`` to your settings and it, as well as ``DUO_CONFIG``, will look more like this::
    
    DUO_LEGACY_PROMPT = True
    DUO_CONFIG = {
        'DEFAULT': {
            'HOST': '<api-host-url>',
            'IKEY': '<integration_key>',
            'AKEY': '<app_secret_key>',
            'SKEY': '<secret_key>',
            'FIRST_STAGE_BACKENDS': [
                'django.contrib.auth.backends.ModelBackend',
            ]
        }
    }

Note the additional ``AKEY`` parameter, which should be a large randomly-generated string, similar to your ``SECRET_KEY``.

----------------------
 First Stage Backends
----------------------

The ``FIRST_STAGE_BACKENDS`` key for each entry in ``DUO_CONFIG`` should be a list of the authentication backends that the Duo application should act as a second factor for. If an authentication backend isn't listed in any ``FIRST_STAGE_BACKENDS`` list, then Duo is disabled.

This behavior can be used to create scenarios where only certain users are required to authenticate with Duo. An example might be where all users of Django's builtin authentication system are required to perform a second factor, but externally authenticated users via LDAP or some other mechanism are not.

Likewise, this feature allows different Duo apps to be tasked with users from separate authentication streams. Take the previous example, only LDAP users are instead required to authenticate against a different institution's Duo application instance.

--------------------
 Username Remapping
--------------------

If it is necessary to remap a user's name to a different name in Duo, you can add the ``USERNAME_REMAPPER`` key to a Duo Config entry. The value of ``USERNAME_REMAPPER`` should be a function, callable object, or a string containing the dotted path to a callable which accepts an HttpRequest object and returns a username string, which will be used in the Duo signing request instead of the name as it appears in ``request.user.username``.

----------------------------------------
 Failing Open (Not supported on LEGACY)
----------------------------------------

By default, if any error occurs communicating with Duo's authentication servers, the authentication attempt is aborted, and the user is logged out. If it is desirable for Duo to be skipped in the event of a communication issue, simply add ``'FAIL_OPEN': True`` to the desired applications in the ``DUO_CONFIG``.

------------------------------------------------
 Overloading the Default Template (LEGACY ONLY)
------------------------------------------------

The Duo login view loads a template named ``duo_auth_form.html`` which must minimally include the following to properly render the Duo I-Frame::

    <form method="POST" id="duo_form">
      {% csrf_token %}
      {% if next %}
        <input type="hidden" name="next" value="{{ next }}"/>
      {% endif %}
      {% if app_name %}
        <input type="hidden" name="app_name" value="{{ app_name }}"/>
      {% endif %}
     </form>

     <link rel="stylesheet" type="text/css" href="{{ duo_css_src }}">
     <script src="{{ duo_js_src }}"></script>
     <iframe id="duo_iframe"
             title="Two-Factor Authentication"
             frameborder="0"
             data-host="{{ duo_host }}"
             data-sig-request="{{ sig_request }}"
             data-post-action="{{ post_action }}"
             >
     </iframe>


