import logging
import os

from django.conf            import settings
from django.contrib.auth    import logout, BACKEND_SESSION_KEY
from django.shortcuts       import render, redirect
from django.views           import View
import duo_web

logger = logging.getLogger(__name__)

class DuoAuthView(View):
    def get(self, request):
        next_url = request.GET.get('next', settings.LOGIN_REDIRECT_URL)
        # Figure out which Duo App applies to the user's backend
        app_name, app = None, None
        for k, v in settings.DUO_CONFIG.items():
            if request.session[BACKEND_SESSION_KEY] in v.get('FIRST_STAGE_BACKENDS',[]):
                app_name, app = k, v
                break
        else:
            # If none, skip Duo
            request.session['DUO_STATUS'] = 'SKIPPED'
            return redirect(next_url)
        
        sig_request = duo_web.sign_request(
            app["IKEY"], app["SKEY"], app["AKEY"], request.user.username
        )
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
        duo_user = duo_web.verify_response(
            settings.DUO_CONFIG[app_name]["IKEY"], settings.DUO_CONFIG[app_name]["SKEY"],
            settings.DUO_CONFIG[app_name]["AKEY"], sig_response
        )

        if duo_user is None or duo_user != request.user.username:
            logger.info('Duo returned {0} instead of {1}'.format(duo_user, request.user.username))
            logout(request)
        else:    
            logger.info('User {0} authenticated using duo'.format(duo_user))
            request.session['DUO_STATUS'] = 'COMPLETED'
        
        return redirect(next_url)

