from abc import ABC, abstractmethod
from typing import Optional, List
from datetime import date
from modules.solicitud.domain.entities.solicitud import Solicitud


class SolicitudRepository(ABC):
    @abstractmethod
    def get_by_id(self, id: int) -> Optional[Solicitud]:
        raise NotImplementedError

    @abstractmethod
    def get_by_empleado(
        self,
        empleado_id: int,
        estado: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> List[Solicitud]:
        raise NotImplementedError

    @abstractmethod
    def get_by_empresa(
        self,
        empresa_id: int,
        estado: Optional[str] = None,
        empleado_id: Optional[int] = None,
        tipo_permiso_id: Optional[int] = None,
        fecha_desde: Optional[date] = None,
        fecha_hasta: Optional[date] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> List[Solicitud]:
        raise NotImplementedError

    @abstractmethod
    def get_aprobadas_en_periodo(
        self, empleado_id: int, fecha_desde: date, fecha_hasta: date
    ) -> List[Solicitud]:
        raise NotImplementedError

    @abstractmethod
    def save(self, solicitud: Solicitud) -> Solicitud:
        raise NotImplementedError

    @abstractmethod
    def count_by_empresa(self, empresa_id: int, estado: Optional[str] = None) -> int:
        raise NotImplementedError