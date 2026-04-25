from shared.application.base_use_case import BaseUseCase
from modules.usuario.domain.repositories.usuario_repository import UsuarioRepository
from modules.usuario.domain.exceptions import UsuarioNoEncontradoException


class BloquearUsuarioUseCase(BaseUseCase[dict, None]):
    def __init__(self, usuario_repository: UsuarioRepository):
        self._usuario_repository = usuario_repository

    def execute(self, input_dto: dict) -> None:
        usuario = self._usuario_repository.get_by_id(input_dto["usuario_id"])
        if not usuario:
            raise UsuarioNoEncontradoException(str(input_dto["usuario_id"]))
        usuario.desbloquear() if input_dto.get("desbloquear") else None
        self._usuario_repository.save(usuario)


class DesbloquearUsuarioUseCase(BaseUseCase[dict, None]):
    def __init__(self, usuario_repository: UsuarioRepository):
        self._usuario_repository = usuario_repository

    def execute(self, input_dto: dict) -> None:
        usuario = self._usuario_repository.get_by_id(input_dto["usuario_id"])
        if not usuario:
            raise UsuarioNoEncontradoException(str(input_dto["usuario_id"]))
        usuario.desbloquear()
        self._usuario_repository.save(usuario)