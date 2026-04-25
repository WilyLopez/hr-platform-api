from shared.application.base_use_case import BaseUseCase
from modules.usuario.domain.repositories.usuario_repository import UsuarioRepository
from modules.usuario.application.dtos.usuario_dto import RecuperarContrasenaInputDTO


class RecuperarContrasenaUseCase(BaseUseCase[RecuperarContrasenaInputDTO, None]):
    def __init__(
        self,
        usuario_repository: UsuarioRepository,
        password_service,
        notificacion_use_case,
    ):
        self._usuario_repository = usuario_repository
        self._password_service = password_service
        self._notificacion_use_case = notificacion_use_case

    def execute(self, input_dto: RecuperarContrasenaInputDTO) -> None:
        usuario = self._usuario_repository.get_by_correo(input_dto.correo)
        if not usuario:
            return

        nueva_contrasena_temporal = self._password_service.generar_temporal()
        nuevo_hash = self._password_service.hash(nueva_contrasena_temporal)
        usuario.cambiar_password(nuevo_hash)
        self._usuario_repository.save(usuario)

        self._notificacion_use_case.enviar_contrasena_temporal(
            correo=input_dto.correo,
            contrasena_temporal=nueva_contrasena_temporal,
        )