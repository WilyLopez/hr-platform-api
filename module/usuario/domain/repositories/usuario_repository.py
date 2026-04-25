from abc import ABC, abstractmethod
from typing import Optional, List
from modules.usuario.domain.entities.usuario import Usuario


class UsuarioRepository(ABC):
    @abstractmethod
    def get_by_id(self, id: int) -> Optional[Usuario]:
        raise NotImplementedError

    @abstractmethod
    def get_by_codigo_unico(self, codigo: str) -> Optional[Usuario]:
        raise NotImplementedError

    @abstractmethod
    def get_by_correo(self, correo: str) -> Optional[Usuario]:
        raise NotImplementedError

    @abstractmethod
    def get_by_empresa(self, empresa_id: int, rol: Optional[str] = None) -> List[Usuario]:
        raise NotImplementedError

    @abstractmethod
    def save(self, usuario: Usuario) -> Usuario:
        raise NotImplementedError

    @abstractmethod
    def exists_by_correo(self, correo: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def exists_by_codigo_unico(self, codigo: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def count_activos_by_empresa(self, empresa_id: int) -> int:
        raise NotImplementedError