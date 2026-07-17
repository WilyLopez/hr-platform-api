from shared.application.base_use_case import BaseUseCase
from modules.usuario.domain.repositories.usuario_repository import UsuarioRepository
from modules.usuario.application.dtos.usuario_dto import CambiarContrasenaInputDTO
from modules.usuario.domain.exceptions import UsuarioNoEncontradoException, CredencialesInvalidasException


class CambiarContrasenaUseCase(BaseUseCase[CambiarContrasenaInputDTO, None]):
    def __init__(self, usuario_repository: UsuarioRepository, password_service, auditoria_use_case=None):
        self._usuario_repository = usuario_repository
        self._password_service = password_service
        self._auditoria_use_case = auditoria_use_case

    def execute(self, input_dto: CambiarContrasenaInputDTO) -> None:
        usuario = self._usuario_repository.get_by_id(input_dto.usuario_id)
        if not usuario:
            raise UsuarioNoEncontradoException()

        # Verificar contraseña actual
        if not self._password_service.verify(input_dto.contrasena_actual, usuario.password_hash):
            raise CredencialesInvalidasException(mensaje="La contraseña actual es incorrecta.")

        if input_dto.contrasena_actual == input_dto.contrasena_nueva:
            raise CredencialesInvalidasException(mensaje="La nueva contraseña debe ser distinta a la actual.")

        # Actualizar contraseña
        nuevo_hash = self._password_service.hash(input_dto.contrasena_nueva)
        usuario.cambiar_password(nuevo_hash)
        
        self._usuario_repository.save(usuario)

        if self._auditoria_use_case:
            from shared.constants import TiposEvento
            self._auditoria_use_case.registrar(
                empresa_id=usuario.empresa_id,
                usuario_id=usuario.id,
                tipo_evento=TiposEvento.MODIFICACION_USUARIO,
                descripcion="Cambio de contraseña exitoso.",
                ip_address=None,
                detalles={"cambio_obligatorio": True}
            )
