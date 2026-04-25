from dataclasses import dataclass
from datetime import datetime, date
from typing import Optional


@dataclass(frozen=True)
class SolicitudCreadaEvent:
    solicitud_id: int
    empresa_id: int
    empleado_id: int
    tipo_permiso: str
    fecha_inicio: date
    fecha_fin: date
    timestamp: datetime


@dataclass(frozen=True)
class SolicitudAprobadaEvent:
    solicitud_id: int
    empresa_id: int
    empleado_id: int
    evaluado_por_id: int
    comentario: Optional[str]
    timestamp: datetime


@dataclass(frozen=True)
class SolicitudRechazadaEvent:
    solicitud_id: int
    empresa_id: int
    empleado_id: int
    evaluado_por_id: int
    comentario: str
    timestamp: datetime