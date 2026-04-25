from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class EnviarEmailInputDTO:
    usuario_id: int
    empresa_id: Optional[int]
    correo_destino: str
    titulo: str
    mensaje: str


@dataclass
class EnviarInAppInputDTO:
    usuario_id: int
    empresa_id: Optional[int]
    titulo: str
    mensaje: str


@dataclass
class ConfigurarPreferenciasInputDTO:
    usuario_id: int
    email_habilitado: bool
    push_habilitado: bool


@dataclass
class NotificacionOutputDTO:
    id: int
    usuario_id: int
    titulo: str
    mensaje: str
    canal: str
    leida: bool
    enviada: bool
    fecha_envio: Optional[datetime]
    fecha_creacion: datetime