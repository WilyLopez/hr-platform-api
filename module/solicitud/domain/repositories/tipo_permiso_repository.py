from abc import ABC, abstractmethod
from typing import Optional, List
from modules.solicitud.domain.entities.tipo_permiso import TipoPermiso


class TipoPermisoRepository(ABC):
    @abstractmethod
    def get_by_id(self, id: int) -> Optional[TipoPermiso]:
        raise NotImplementedError

    @abstractmethod
    def get_by_empresa(self, empresa_id: int, solo_activos: bool = True) -> List[TipoPermiso]:
        raise NotImplementedError

    @abstractmethod
    def save(self, tipo_permiso: TipoPermiso) -> TipoPermiso:
        raise NotImplementedError

    @abstractmethod
    def exists(self, id: int) -> bool:
        raise NotImplementedError