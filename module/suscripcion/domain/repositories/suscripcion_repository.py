from abc import ABC, abstractmethod
from typing import Optional, List
from datetime import datetime
from modules.suscripcion.domain.entities.suscripcion import Suscripcion


class SuscripcionRepository(ABC):
    @abstractmethod
    def get_by_id(self, id: int) -> Optional[Suscripcion]:
        raise NotImplementedError

    @abstractmethod
    def get_by_empresa(self, empresa_id: int) -> Optional[Suscripcion]:
        raise NotImplementedError

    @abstractmethod
    def get_trials_por_vencer(self, dias: int) -> List[Suscripcion]:
        raise NotImplementedError

    @abstractmethod
    def get_vencidas_sin_pago(self, dias_gracia: int) -> List[Suscripcion]:
        raise NotImplementedError

    @abstractmethod
    def save(self, suscripcion: Suscripcion) -> Suscripcion:
        raise NotImplementedError

    @abstractmethod
    def exists_by_empresa(self, empresa_id: int) -> bool:
        raise NotImplementedError