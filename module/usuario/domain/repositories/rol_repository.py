from abc import ABC, abstractmethod
from typing import Optional, List
from modules.usuario.domain.entities.rol import Rol


class RolRepository(ABC):
    @abstractmethod
    def get_by_id(self, id: int) -> Optional[Rol]:
        raise NotImplementedError

    @abstractmethod
    def get_by_nombre(self, nombre: str, empresa_id: Optional[int] = None) -> Optional[Rol]:
        raise NotImplementedError

    @abstractmethod
    def get_by_empresa(self, empresa_id: int) -> List[Rol]:
        raise NotImplementedError

    @abstractmethod
    def save(self, rol: Rol) -> Rol:
        raise NotImplementedError

    @abstractmethod
    def exists(self, id: int) -> bool:
        raise NotImplementedError