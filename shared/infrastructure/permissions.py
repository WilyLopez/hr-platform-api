from rest_framework.permissions import BasePermission
from shared.constants import EstadosSeguridadUsuario

class RequirePasswordChangePermission(BasePermission):
    """
    Permiso que bloquea el acceso si el usuario tiene el flag de
    'PASSWORD_CHANGE_REQUIRED', a menos que sea a las rutas de cambio de contraseña o logout.
    """
    message = "PASSWORD_CHANGE_REQUIRED"
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return True # Let IsAuthenticated handle it
            
        # Rutas exceptuadas del bloqueo
        # Por ejemplo: GET /api/v1/usuarios/perfil/, PUT /api/v1/usuarios/perfil/contrasena/
        # y POST /api/v1/auth/logout/
        exempt_views = ["UsuarioPerfilView", "CambiarContrasenaView", "LogoutView", "LoginView", "RefrescarTokenView"]
        if view.__class__.__name__ in exempt_views:
            return True
            
        # Si el usuario tiene que cambiar la contraseña, denegar acceso.
        # Check against database because the JWT token might be cached
        # However, for performance we could rely on token or user object if attached
        if hasattr(request.user, "estado_seguridad"):
            return request.user.estado_seguridad != EstadosSeguridadUsuario.PASSWORD_CHANGE_REQUIRED
            
        return True
