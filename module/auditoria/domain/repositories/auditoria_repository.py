from abc import ABC, abstractmethod
from typing import Optional, List
from datetime import datetime
from modules.auditoria.domain.entities.registro_auditoria import RegistroAuditoria


class AuditoriaRepository(ABC):
    @abstractmethod
    def get_by_id(self, id: int) -> Optional[RegistroAuditoria]:
        raise NotImplementedError

    @abstractmethod
    def get_global(
        self,
        empresa_id: Optional[int] = None,
        usuario_id: Optional[int] = None,
        rol: Optional[str] = None,
        tipo_evento: Optional[str] = None,
        fecha_desde: Optional[datetime] = None,
        fecha_hasta: Optional[datetime] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> List[RegistroAuditoria]:
        raise NotImplementedError

    @abstractmethod
    def get_by_empresa(
        self,
        empresa_id: int,
        usuario_id: Optional[int] = None,
        tipo_evento: Optional[str] = None,
        fecha_desde: Optional[datetime] = None,
        fecha_hasta: Optional[datetime] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> List[RegistroAuditoria]:
        raise NotImplementedError

    @abstractmethod
    def save(self, registro: RegistroAuditoria) -> RegistroAuditoria:
        raise NotImplementedError

    @abstractmethod
    def count_global(
        self,
        empresa_id: Optional[int] = None,
        fecha_desde: Optional[datetime] = None,
        fecha_hasta: Optional[datetime] = None,
    ) -> int:
        raise NotImplementedError

    @abstractmethod
    def eliminar_anteriores_a(self, fecha_limite: datetime) -> int:
        raise NotImplementedError