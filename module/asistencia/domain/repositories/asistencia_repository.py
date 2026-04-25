from abc import ABC, abstractmethod
from typing import Optional, List
from datetime import date
from modules.asistencia.domain.entities.registro_asistencia import RegistroAsistencia


class AsistenciaRepository(ABC):
    @abstractmethod
    def get_by_id(self, id: int) -> Optional[RegistroAsistencia]:
        raise NotImplementedError

    @abstractmethod
    def get_by_empleado(
        self,
        empleado_id: int,
        fecha_desde: Optional[date] = None,
        fecha_hasta: Optional[date] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> List[RegistroAsistencia]:
        raise NotImplementedError

    @abstractmethod
    def get_by_empresa(
        self,
        empresa_id: int,
        fecha: Optional[date] = None,
        sede_id: Optional[int] = None,
        area: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> List[RegistroAsistencia]:
        raise NotImplementedError

    @abstractmethod
    def get_ultimo_marcaje_del_dia(self, empleado_id: int, fecha: date) -> Optional[RegistroAsistencia]:
        raise NotImplementedError

    @abstractmethod
    def existe_marcaje_tipo_en_fecha(self, empleado_id: int, tipo: str, fecha: date) -> bool:
        raise NotImplementedError

    @abstractmethod
    def save(self, registro: RegistroAsistencia) -> RegistroAsistencia:
        raise NotImplementedError

    @abstractmethod
    def count_by_empresa(
        self,
        empresa_id: int,
        fecha_desde: Optional[date] = None,
        fecha_hasta: Optional[date] = None,
    ) -> int:
        raise NotImplementedError