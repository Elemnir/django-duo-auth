from django.conf        import settings
from django.shortcuts   import redirect
from django.urls        import reverse

class DuoAuthMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith(settings.STATIC_URL):
            return self.get_response(request)

        if request.user.is_authenticated and 'DUO_STATUS' not in request.session:
            request.session['DUO_STATUS'] = 'IN_PROGRESS'
            return redirect(reverse('duo_auth:duo_login') + "?next=" + request.path)
        
        if (request.user.is_authenticated
                and request.session.get('DUO_STATUS', 'IN_PROGRESS') == 'IN_PROGRESS'
                and reverse('duo_auth:duo_login') not in request.path):
            return redirect(reverse('duo_auth:duo_login') + "?next=" + request.path)

        return self.get_response(request)
