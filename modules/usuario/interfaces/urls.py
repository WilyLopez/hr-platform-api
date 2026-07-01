from django.urls import path
from modules.usuario.interfaces.views.auth_view import (
    LoginView, RefrescarTokenView, LogoutView, RecuperarContrasenaView
)
from modules.usuario.interfaces.views.usuario_view import (
    UsuarioPerfilView, CambiarContrasenaView
)

urlpatterns = [
    path("login/", LoginView.as_view()),
    path("token/refresh/", RefrescarTokenView.as_view()),
    path("logout/", LogoutView.as_view()),
    path("recuperar-contrasena/", RecuperarContrasenaView.as_view()),
    path("perfil/", UsuarioPerfilView.as_view()),
    path("perfil/cambiar-contrasena/", CambiarContrasenaView.as_view()),
]