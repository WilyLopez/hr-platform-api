from abc import ABC, abstractmethod
from typing import Optional, List
from modules.suscripcion.domain.entities.plan import Plan


class PlanRepository(ABC):
    @abstractmethod
    def get_by_id(self, id: int) -> Optional[Plan]:
        raise NotImplementedError

    @abstractmethod
    def get_by_nombre(self, nombre: str) -> Optional[Plan]:
        raise NotImplementedError

    @abstractmethod
    def get_all_activos(self) -> List[Plan]:
        raise NotImplementedError

    @abstractmethod
    def save(self, plan: Plan) -> Plan:
        raise NotImplementedError

    @abstractmethod
    def exists(self, id: int) -> bool:
        raise NotImplementedError