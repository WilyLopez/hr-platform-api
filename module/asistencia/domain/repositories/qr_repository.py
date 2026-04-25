from abc import ABC, abstractmethod
from typing import Optional
from modules.asistencia.domain.entities.token_qr import TokenQr


class QrRepository(ABC):
    @abstractmethod
    def get_by_token(self, token: str) -> Optional[TokenQr]:
        raise NotImplementedError

    @abstractmethod
    def get_vigente_by_sede(self, sede_id: int) -> Optional[TokenQr]:
        raise NotImplementedError

    @abstractmethod
    def save(self, token_qr: TokenQr) -> TokenQr:
        raise NotImplementedError

    @abstractmethod
    def invalidar_por_sede(self, sede_id: int) -> None:
        raise NotImplementedError