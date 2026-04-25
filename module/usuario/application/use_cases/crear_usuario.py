from datetime import datetime
from shared.application.base_use_case import BaseUseCase
from shared.domain.value_objects import Email, CodigoUnico
from shared.constants import EstadosUsuario, TiposEvento
from modules.usuario.domain.entities.usuario import Usuario
from modules.usuario.domain.repositories.usuario_repository import UsuarioRepository
from modules.usuario.domain.repositories.rol_repository import RolRepository
from modules.usuario.domain.exceptions import RolNoEncontradoException
from shared.domain.exceptions import EntityAlreadyExistsException
from modules.usuario.application.dtos.usuario_dto import CrearUsuarioInputDTO, UsuarioOutputDTO


class CrearUsuarioUseCase(BaseUseCase[CrearUsuarioInputDTO, UsuarioOutputDTO]):
    def __init__(
        self,
        usuario_repository: UsuarioRepository,
        rol_repository: RolRepository,
        password_service,
        auditoria_use_case,
    ):
        self._usuario_repository = usuario_repository
        self._rol_repository = rol_repository
        self._password_service = password_service
        self._auditoria_use_case = auditoria_use_case

    def execute(self, input_dto: CrearUsuarioInputDTO) -> UsuarioOutputDTO:
        if self._usuario_repository.exists_by_correo(input_dto.correo):
            raise EntityAlreadyExistsException("Usuario", "correo", input_dto.correo)

        rol = self._rol_repository.get_by_nombre(input_dto.rol_nombre, input_dto.empresa_id)
        if not rol:
            raise RolNoEncontradoException(input_dto.rol_nombre)

        codigo_unico = self._generar_codigo_unico()
        password_hash = self._password_service.hash(input_dto.contrasena)

        usuario = Usuario(
            id=None,
            empresa_id=input_dto.empresa_id,
            rol_id=rol.id,
            codigo_unico=codigo_unico,
            correo=Email(input_dto.correo),
            password_hash=password_hash,
            estado=EstadosUsuario.ACTIVO,
            intentos_fallidos=0,
            ultimo_acceso=None,
            fecha_creacion=datetime.now(),
            fecha_actualizacion=None,
        )

        usuario = self._usuario_repository.save(usuario)

        self._auditoria_use_case.registrar(
            empresa_id=input_dto.empresa_id,
            usuario_id=usuario.id,
            tipo_evento=TiposEvento.CREACION_USUARIO,
            descripcion=f"Usuario creado con rol {input_dto.rol_nombre}.",
            ip_address=None,
            detalles={"rol": input_dto.rol_nombre, "correo": input_dto.correo},
        )

        return UsuarioOutputDTO(
            id=usuario.id,
            empresa_id=usuario.empresa_id,
            codigo_unico=str(usuario.codigo_unico),
            correo=str(usuario.correo),
            rol=input_dto.rol_nombre,
            estado=usuario.estado,
            ultimo_acceso=usuario.ultimo_acceso,
            fecha_creacion=usuario.fecha_creacion,
        )

    def _generar_codigo_unico(self) -> CodigoUnico:
        while True:
            codigo = CodigoUnico.generate()
            if not self._usuario_repository.exists_by_codigo_unico(str(codigo)):
                return codigo