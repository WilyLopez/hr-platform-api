from abc import ABC, abstractmethod
from typing import Optional, List
from modules.notificacion.domain.entities.notificacion import Notificacion


class NotificacionRepository(ABC):
    @abstractmethod
    def get_by_id(self, id: int) -> Optional[Notificacion]:
        raise NotImplementedError

    @abstractmethod
    def get_by_usuario(
        self,
        usuario_id: int,
        solo_no_leidas: bool = False,
        page: int = 1,
        page_size: int = 20,
    ) -> List[Notificacion]:
        raise NotImplementedError

    @abstractmethod
    def save(self, notificacion: Notificacion) -> Notificacion:
        raise NotImplementedError

    @abstractmethod
    def count_no_leidas(self, usuario_id: int) -> int:
        raise NotImplementedError