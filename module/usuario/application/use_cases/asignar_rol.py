from shared.application.base_use_case import BaseUseCase
from modules.usuario.domain.repositories.usuario_repository import UsuarioRepository
from modules.usuario.domain.repositories.rol_repository import RolRepository
from modules.usuario.domain.exceptions import UsuarioNoEncontradoException, RolNoEncontradoException


class AsignarRolUseCase(BaseUseCase[dict, None]):
    def __init__(
        self,
        usuario_repository: UsuarioRepository,
        rol_repository: RolRepository,
    ):
        self._usuario_repository = usuario_repository
        self._rol_repository = rol_repository

    def execute(self, input_dto: dict) -> None:
        usuario = self._usuario_repository.get_by_id(input_dto["usuario_id"])
        if not usuario:
            raise UsuarioNoEncontradoException(str(input_dto["usuario_id"]))

        rol = self._rol_repository.get_by_id(input_dto["rol_id"])
        if not rol:
            raise RolNoEncontradoException(str(input_dto["rol_id"]))

        usuario.rol_id = rol.id
        self._usuario_repository.save(usuario)