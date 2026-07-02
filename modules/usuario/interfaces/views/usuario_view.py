from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from modules.usuario.infrastructure.repositories.usuario_repository_impl import DjangoUsuarioRepository
from modules.usuario.interfaces.serializers.usuario_serializer import UsuarioOutputSerializer
from modules.usuario.interfaces.serializers.auth_serializer import CambiarContrasenaSerializer
from modules.usuario.application.dtos.usuario_dto import UsuarioOutputDTO, CambiarContrasenaInputDTO
from modules.usuario.application.use_cases.cambiar_contrasena import CambiarContrasenaUseCase
from modules.usuario.infrastructure.services.jwt_service import PasswordService


class UsuarioPerfilView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        repo = DjangoUsuarioRepository()
        usuario = repo.get_by_id(request.user.id)
        if not usuario:
            return Response({"detail": "Usuario no encontrado"}, status=status.HTTP_404_NOT_FOUND)
        
        dto = UsuarioOutputDTO(
            id=usuario.id,
            empresa_id=usuario.empresa_id,
            codigo_unico=str(usuario.codigo_unico.valor) if hasattr(usuario.codigo_unico, 'valor') else str(usuario.codigo_unico),
            correo=str(usuario.correo.valor) if hasattr(usuario.correo, 'valor') else str(usuario.correo),
            rol=request.user.rol,
            estado=usuario.estado,
            ultimo_acceso=usuario.ultimo_acceso,
            fecha_creacion=usuario.fecha_creacion,
        )
        serializer = UsuarioOutputSerializer(dto)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CambiarContrasenaView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        serializer = CambiarContrasenaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        use_case = CambiarContrasenaUseCase(
            usuario_repository=DjangoUsuarioRepository(),
            password_service=PasswordService()
        )
        
        input_dto = CambiarContrasenaInputDTO(
            usuario_id=request.user.id,
            contrasena_actual=serializer.validated_data["contrasena_actual"],
            contrasena_nueva=serializer.validated_data["contrasena_nueva"]
        )
        use_case.execute(input_dto)
        
        return Response({"status": "ok", "message": "Contraseña actualizada exitosamente"})
