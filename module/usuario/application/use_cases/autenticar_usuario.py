from shared.application.base_use_case import BaseUseCase
from shared.constants import TiposEvento
from modules.usuario.domain.repositories.usuario_repository import UsuarioRepository
from modules.usuario.domain.repositories.rol_repository import RolRepository
from modules.usuario.domain.exceptions import UsuarioNoEncontradoException, CredencialesInvalidasException
from modules.usuario.application.dtos.token_dto import AutenticarUsuarioInputDTO, TokenOutputDTO


class AutenticarUsuarioUseCase(BaseUseCase[AutenticarUsuarioInputDTO, TokenOutputDTO]):
    def __init__(
        self,
        usuario_repository: UsuarioRepository,
        rol_repository: RolRepository,
        password_service,
        jwt_service,
        auditoria_use_case,
    ):
        self._usuario_repository = usuario_repository
        self._rol_repository = rol_repository
        self._password_service = password_service
        self._jwt_service = jwt_service
        self._auditoria_use_case = auditoria_use_case

    def execute(self, input_dto: AutenticarUsuarioInputDTO) -> TokenOutputDTO:
        usuario = self._usuario_repository.get_by_codigo_unico(input_dto.codigo_unico)
        if not usuario:
            raise CredencialesInvalidasException()

        usuario.verificar_puede_autenticarse()

        if not self._password_service.verify(input_dto.contrasena, usuario.password_hash):
            usuario.registrar_intento_fallido()
            self._usuario_repository.save(usuario)
            self._auditoria_use_case.registrar(
                empresa_id=usuario.empresa_id,
                usuario_id=usuario.id,
                tipo_evento=TiposEvento.INTENTO_FALLIDO,
                descripcion="Intento de autenticación fallido.",
                ip_address=input_dto.ip_address,
                detalles={"intentos": usuario.intentos_fallidos},
            )
            raise CredencialesInvalidasException()

        usuario.registrar_acceso_exitoso()
        self._usuario_repository.save(usuario)

        rol = self._rol_repository.get_by_id(usuario.rol_id)
        tokens = self._jwt_service.generar_tokens(usuario, rol.nombre)

        self._auditoria_use_case.registrar(
            empresa_id=usuario.empresa_id,
            usuario_id=usuario.id,
            tipo_evento=TiposEvento.INICIO_SESION,
            descripcion="Inicio de sesión exitoso.",
            ip_address=input_dto.ip_address,
            detalles={},
        )

        return TokenOutputDTO(
            access=tokens["access"],
            refresh=tokens["refresh"],
            usuario_id=usuario.id,
            codigo_unico=str(usuario.codigo_unico),
            empresa_id=usuario.empresa_id,
            rol=rol.nombre,
        )