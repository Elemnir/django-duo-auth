"""
    duo_auth.views
    ~~~~~~~~~~~~~~

    This module defines the views which implement the Duo Universal Prompt
    API for performing second-stage user authentication. Users MUST have 
    already logged in using a first stage authentication backend.

"""
import logging

from django.conf import settings
from django.contrib.auth import logout, BACKEND_SESSION_KEY
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.module_loading import import_string
from django.views import View

from duo_universal.client import Client, DuoException


logger = logging.getLogger(__name__)


def first_existing(mapping, keys):
    """Returns the value of the first key in keys which exists in mapping"""
    for key in keys:
        if key in mapping:
            return mapping[key]
    return None


def get_username(app, request):
    """Given a Duo app config and the in-flight request, determine what
    username should be used for identifying the currently authenticating 
    user. If a USERNAME_REMAPPER function is defined for the app, it will
    be invoked and passed the in-flight request and expected to return a
    string.
    """
    username_callable = lambda r: r.user.username
    if 'USERNAME_REMAPPER' in app:
        ur = app['USERNAME_REMAPPER']
        username_callable = ur if callable(ur) else import_string(ur)
    logger.debug('Invoking username mapper: %s', username_callable)
    return username_callable(request)


def prepare_duo_client(request):
    """Given the in-flight request, determine a which, if any, configured
    Duo apps is appropriate for second-stage authentication based on what
    was used first, returning the app's configuration and a Client
    """
    app_name, app = None, None
    auth_backend = request.session[BACKEND_SESSION_KEY]
    logger.debug(
        'Checking for Duo app to follow after backend: %s', auth_backend
    )
    for k, v in settings.DUO_CONFIG.items():
        if auth_backend in v.get('FIRST_STAGE_BACKENDS',[]):
            app_name, app = k, v
            break
    else:
        return None, None

    logger.debug('Backend matched for Duo app: %s', app_name)
    return app, Client(
        client_id = first_existing(app, ["CLIENT_ID", "IKEY"]),
        client_secret = first_existing(app, ["CLIENT_SECRET", "SKEY"]),
        host = first_existing(app, ["API_HOSTNAME", "HOST"]),
        redirect_uri = reverse('duo_auth:duo_callback'),
    )


class DuoAuthView(LoginRequiredMixin, View):
    """View for initiating Duo authentication invoked by the
    DuoAuthMiddleware. Either determines Duo is unnecessary, or
    redirects to a Duo Universal Prompt endpoint
    """
    def get(self, request):
        next_url = request.GET.get('next', settings.LOGIN_REDIRECT_URL)
        request.session['POST_AUTH_URL'] = next_url
        app, client = prepare_duo_client(request)
        if client is None:
            # If none, skip Duo
            request.session['DUO_STATUS'] = 'SKIPPED'
            return redirect(next_url)

        request.session['DUO_USERNAME'] = get_username(app, request)
        try:
            client.health_check()
        except DuoException:
            if app.get('FAIL_OPEN', False):
                logger.warning('Duo failed health check, skipping due to FAIL_OPEN')
                request.session['DUO_STATUS'] = 'SKIPPED'
                return redirect(next_url)
            logger.error('Duo failed health check, disallowing login')
            logout(request)

        logger.debug('Preparing state and redirecting to Duo...')
        request.session["DUO_STATE"] = client.generate_state()
        return redirect(
            client.create_auth_url(
                request.session['DUO_USERNAME'], request.session['DUO_STATE']
            )
        )


class DuoCallbackView(LoginRequiredMixin, View):
    """Callback view for Duo after completing the universal prompt"""
    def get(self, request):
        if ('DUO_STATE' not in request.session
                or 'state' not in request.GET
                or 'duo_code' not in request.GET
                or request.session['DUO_STATE'] != request.GET['state']):
            logger.info('Malformed request to Duo callback endpoint')
            logout(request)

        app, client = prepare_duo_client(request)
        client.exchange_authorization_code_for_2fa_result(
            request.GET['duo_code'], get_username(app, request)
        )
        request.session['DUO_STATUS'] = 'COMPLETED'
        return redirect(
            request.session.get('POST_AUTH_URL', settings.LOGIN_REDIRECT_URL)
        )
