from shared.domain.value_objects import CodigoUnico
from modules.usuario.domain.repositories.usuario_repository import UsuarioRepository


class CodigoUnicoService:
    def __init__(self, usuario_repository: UsuarioRepository):
        self._usuario_repository = usuario_repository

    def generar(self) -> CodigoUnico:
        for _ in range(10):
            codigo = CodigoUnico.generate()
            if not self._usuario_repository.exists_by_codigo_unico(str(codigo)):
                return codigo
        raise RuntimeError("No se pudo generar un código único disponible tras 10 intentos.")