from abc import ABC, abstractmethod
from typing import Optional, List
from modules.empleado.domain.entities.empleado import Empleado


class EmpleadoRepository(ABC):
    @abstractmethod
    def get_by_id(self, id: int) -> Optional[Empleado]:
        raise NotImplementedError

    @abstractmethod
    def get_by_codigo_unico(self, codigo: str) -> Optional[Empleado]:
        raise NotImplementedError

    @abstractmethod
    def get_by_empresa(
        self,
        empresa_id: int,
        estado: Optional[str] = None,
        area: Optional[str] = None,
        sede_id: Optional[int] = None,
        search: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> List[Empleado]:
        raise NotImplementedError

    @abstractmethod
    def save(self, empleado: Empleado) -> Empleado:
        raise NotImplementedError

    @abstractmethod
    def exists_by_documento(self, empresa_id: int, numero_documento: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def exists_by_correo(self, empresa_id: int, correo: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def count_activos_by_empresa(self, empresa_id: int) -> int:
        raise NotImplementedError

    @abstractmethod
    def count_by_empresa(self, empresa_id: int, estado: Optional[str] = None) -> int:
        raise NotImplementedError