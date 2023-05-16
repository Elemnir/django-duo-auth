from django.conf import settings
from django.urls import path

app_name = "duo_auth"

if hasattr(settings, "DUO_LEGACY_PROMPT") and settings.DUO_LEGACY_PROMPT:
    from .legacy_views import DuoAuthView
    urlpatterns = [
        path('login/', DuoAuthView.as_view(), name="duo_login"),
    ]
else:
    from .views import DuoAuthView, DuoCallbackView
    urlpatterns = [
        path('login/', DuoAuthView.as_view(), name="duo_login"),
        path('callback/', DuoCallbackView.as_view(), name="duo_callback"),
    ]
