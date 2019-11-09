from django.urls import path
from .views import DuoAuthView

app_name = "duo_auth"

urlpatterns = [
    path('login/', DuoAuthView.as_view(), name="duo_login"),
]
