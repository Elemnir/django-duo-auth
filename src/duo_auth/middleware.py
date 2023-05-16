"""
    duo_auth.middleware
    ~~~~~~~~~~~~~~~~~~~

    This module implements the middleware for catching requests from 
    users who need to authenticate with Duo, and reroutes them 
    appropriately.
"""

from django.conf        import settings
from django.shortcuts   import redirect
from django.urls        import reverse

class DuoAuthMiddleware:
    """Implements the Django middleware pattern, using the session state
    to determine if further authentication is necessary and rerouting
    requests when needed. Intentionally attempts to ignore static assests
    that can cause rendering errors for in-flight authentication attempts
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip for static assests
        if request.path.startswith(settings.STATIC_URL):
            return self.get_response(request)

        # Skip if you're going to the callback page
        if (not getattr(settings, 'DUO_LEGACY_PROMPT', False)
                and reverse('duo_auth:duo_callback') in request.path):
            return self.get_response(request)

        # Catch authenticated, but not Duo authenticated, users and send them to Duo
        if (request.user.is_authenticated
                and request.session.get('DUO_STATUS', '') not in ('COMPLETED', 'SKIPPED')
                and reverse('duo_auth:duo_login') not in request.path):
            return redirect(reverse('duo_auth:duo_login') + "?next=" + request.path)

        return self.get_response(request)
