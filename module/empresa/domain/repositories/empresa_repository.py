from abc import ABC, abstractmethod
from typing import Optional, List
from modules.empresa.domain.entities.empresa import Empresa


class EmpresaRepository(ABC):
    @abstractmethod
    def get_by_id(self, id: int) -> Optional[Empresa]:
        raise NotImplementedError

    @abstractmethod
    def get_by_ruc(self, ruc: str) -> Optional[Empresa]:
        raise NotImplementedError

    @abstractmethod
    def get_all(self, estado: Optional[str] = None, page: int = 1, page_size: int = 20) -> List[Empresa]:
        raise NotImplementedError

    @abstractmethod
    def save(self, empresa: Empresa) -> Empresa:
        raise NotImplementedError

    @abstractmethod
    def exists_by_ruc(self, ruc: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def count_all(self, estado: Optional[str] = None) -> int:
        raise NotImplementedError