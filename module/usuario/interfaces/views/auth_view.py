from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny

from modules.usuario.interfaces.serializers.auth_serializer import (
    LoginSerializer,
    TokenOutputSerializer,
    RefrescarTokenSerializer,
    RecuperarContrasenaSerializer,
)
from modules.usuario.application.dtos.token_dto import AutenticarUsuarioInputDTO, RefrescarTokenInputDTO
from modules.usuario.application.dtos.usuario_dto import RecuperarContrasenaInputDTO
from modules.usuario.infrastructure.repositories.usuario_repository_impl import DjangoUsuarioRepository
from modules.usuario.infrastructure.repositories.rol_repository_impl import DjangoRolRepository
from modules.usuario.infrastructure.services.jwt_service import JwtService, PasswordService
from modules.usuario.application.use_cases.autenticar_usuario import AutenticarUsuarioUseCase
from modules.usuario.application.use_cases.refrescar_token import RefrescarTokenUseCase
from modules.usuario.application.use_cases.cerrar_sesion import CerrarSesionUseCase
from modules.usuario.application.use_cases.recuperar_contrasena import RecuperarContrasenaUseCase
from modules.auditoria.infrastructure.repositories.auditoria_repository_impl import DjangoAuditoriaRepository
from modules.auditoria.application.use_cases.registrar_evento import RegistrarEventoUseCase
from modules.notificacion.infrastructure.services.email_service import EmailService


def _auditoria():
    return RegistrarEventoUseCase(DjangoAuditoriaRepository())


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        d = serializer.validated_data
        use_case = AutenticarUsuarioUseCase(
            usuario_repository=DjangoUsuarioRepository(),
            rol_repository=DjangoRolRepository(),
            password_service=PasswordService(),
            jwt_service=JwtService(),
            auditoria_use_case=_auditoria(),
        )
        output = use_case.execute(AutenticarUsuarioInputDTO(
            codigo_unico=d["codigo_unico"],
            contrasena=d["contrasena"],
            ip_address=request.META.get("REMOTE_ADDR", ""),
        ))
        return Response(TokenOutputSerializer(output).data)


class RefrescarTokenView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RefrescarTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        use_case = RefrescarTokenUseCase(JwtService())
        output = use_case.execute(RefrescarTokenInputDTO(
            refresh=serializer.validated_data["refresh"]
        ))
        return Response({"access": output.access})


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        use_case = CerrarSesionUseCase(JwtService(), _auditoria())
        use_case.execute({
            "refresh_token": request.data.get("refresh"),
            "usuario_id": request.usuario_id,
            "empresa_id": request.empresa_id,
            "ip_address": request.META.get("REMOTE_ADDR"),
        })
        return Response({"status": "ok"})


class RecuperarContrasenaView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RecuperarContrasenaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        class _NotifAdapter:
            def __init__(self, svc):
                self._svc = svc

            def enviar_contrasena_temporal(self, correo, contrasena_temporal):
                self._svc.notificar_contrasena_temporal(correo, contrasena_temporal)

        use_case = RecuperarContrasenaUseCase(
            usuario_repository=DjangoUsuarioRepository(),
            password_service=PasswordService(),
            notificacion_use_case=_NotifAdapter(EmailService()),
        )
        use_case.execute(RecuperarContrasenaInputDTO(
            correo=serializer.validated_data["correo"]
        ))
        return Response({"status": "ok", "message": "Si el correo existe, recibirás instrucciones."})