from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("registro/", views.registro_view, name="registro"),
    path(
        "iniciar-sesion/",
        LoginView.as_view(template_name="accounts/login.html"),
        name="login",
    ),
    path("panel/", views.panel_view, name="panel"),
    path("cerrar-sesion/", LogoutView.as_view(), name="logout"),
]
