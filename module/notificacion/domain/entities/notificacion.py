from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Notificacion:
    id: Optional[int]
    empresa_id: Optional[int]
    usuario_id: int
    titulo: str
    mensaje: str
    canal: str
    leida: bool
    enviada: bool
    fecha_envio: Optional[datetime]
    fecha_lectura: Optional[datetime]
    fecha_creacion: datetime

    CANAL_EMAIL = "EMAIL"
    CANAL_IN_APP = "IN_APP"
    CANAL_PUSH = "PUSH"

    def marcar_como_enviada(self) -> None:
        self.enviada = True
        self.fecha_envio = datetime.now()

    def marcar_como_leida(self) -> None:
        self.leida = True
        self.fecha_lectura = datetime.now()

    def es_email(self) -> bool:
        return self.canal == self.CANAL_EMAIL

    def es_in_app(self) -> bool:
        return self.canal == self.CANAL_IN_APP

    def es_push(self) -> bool:
        return self.canal == self.CANAL_PUSH