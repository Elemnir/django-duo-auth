import logging
import os

from django.conf                    import settings
from django.contrib.auth            import logout, BACKEND_SESSION_KEY
from django.contrib.auth.mixins     import LoginRequiredMixin
from django.shortcuts               import render, redirect
from django.utils.module_loading    import import_string
from django.views                   import View
import duo_web

logger = logging.getLogger(__name__)

class DuoAuthView(LoginRequiredMixin, View):
    def get_username(self, app, request):
        username_callable = lambda r: r.user.username
        if 'USERNAME_REMAPPER' in app:
            ur = app['USERNAME_REMAPPER']
            username_callable = ur if callable(ur) else import_string(ur)
        logger.debug('Invoking username mapper: {0}'.format(username_callable))
        return username_callable(request)


    def get(self, request):
        next_url = request.GET.get('next', settings.LOGIN_REDIRECT_URL)
        # Figure out which Duo App applies to the user's backend
        app_name, app = None, None
        auth_backend = request.session[BACKEND_SESSION_KEY]
        logger.debug(
            'Checking for Duo app to follow after backend: {0}'.format(auth_backend)
        )
        for k, v in settings.DUO_CONFIG.items():
            if auth_backend in v.get('FIRST_STAGE_BACKENDS',[]):
                app_name, app = k, v
                break
        else:
            # If none, skip Duo
            request.session['DUO_STATUS'] = 'SKIPPED'
            return redirect(next_url)
        
        username = self.get_username(app, request)
        sig_request = duo_web.sign_request(
            app["IKEY"], app["SKEY"], app["AKEY"], username
        )
        logger.info('User {0} started Duo using app {1}'.format(username, app_name))
        return render(request, 'duo_auth_form.html', {
            'duo_css_src': os.path.join(settings.STATIC_URL, 'css', 'Duo-Frame.css'),
            'duo_js_src': os.path.join(settings.STATIC_URL, 'javascript', 'Duo-Web-v2.js'),
            'app_name': app_name,
            'next': next_url,
            'duo_host': app["HOST"],
            'post_action': request.path,
            'sig_request': sig_request
        })
    

    def post(self, request):
        sig_response = request.POST.get('sig_response', '')
        app_name = request.POST.get('app_name', 'DEFAULT')
        next_url = request.POST.get('next', settings.LOGIN_REDIRECT_URL)
        username = self.get_username(settings.DUO_CONFIG[app_name], request)
        duo_user = duo_web.verify_response(
            settings.DUO_CONFIG[app_name]["IKEY"], settings.DUO_CONFIG[app_name]["SKEY"],
            settings.DUO_CONFIG[app_name]["AKEY"], sig_response
        )
 
        if duo_user is None or duo_user != username:
            logger.info('Duo returned {0} instead of {1}'.format(duo_user, username))
            logout(request)
        else:    
            logger.info('User {0} authenticated using duo'.format(duo_user))
            request.session['DUO_STATUS'] = 'COMPLETED'
        
        return redirect(next_url)

