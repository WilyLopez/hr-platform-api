from django.utils.deprecation import MiddlewareMixin
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError


class JwtMiddleware(MiddlewareMixin):
    def process_request(self, request):
        auth_header = request.META.get("HTTP_AUTHORIZATION", "")
        if not auth_header:
            return

        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return

        try:
            token = JWTAuthentication().get_validated_token(parts[1])
            request.empresa_id = token.get("empresa_id")
            request.rol = token.get("rol")
            request.usuario_id = token.get("usuario_id")
            
            if request.empresa_id:
                from modules.empresa.infrastructure.repositories.empresa_repository_impl import DjangoEmpresaRepository
                repo = DjangoEmpresaRepository()
                empresa = repo.get_by_id(request.empresa_id)
                # Bloquear acceso si la empresa no esta activa ni en prueba
                if empresa and empresa.estado in ["SUSPENDIDA", "CANCELADA", "BLOQUEADA"]:
                    from django.http import JsonResponse
                    return JsonResponse({
                        "code": "COMPANY_SUSPENDED", 
                        "error": "La empresa se encuentra suspendida o bloqueada."
                    }, status=403)
                    
        except (InvalidToken, TokenError):
            pass