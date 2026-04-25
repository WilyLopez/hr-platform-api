from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional


@dataclass
class CrearSolicitudInputDTO:
    empleado_id: int
    empresa_id: int
    tipo_permiso_id: int
    fecha_inicio: date
    fecha_fin: date
    motivo: str
    adjunto_url: Optional[str]


@dataclass
class EvaluarSolicitudInputDTO:
    solicitud_id: int
    empresa_id: int
    evaluado_por_id: int
    comentario: Optional[str]


@dataclass
class ListarSolicitudesInputDTO:
    empresa_id: int
    empleado_id: Optional[int] = None
    estado: Optional[str] = None
    tipo_permiso_id: Optional[int] = None
    fecha_desde: Optional[date] = None
    fecha_hasta: Optional[date] = None
    page: int = 1
    page_size: int = 20


@dataclass
class SolicitudOutputDTO:
    id: int
    empresa_id: int
    empleado_id: int
    empleado_nombre: str
    tipo_permiso_id: int
    tipo_permiso_nombre: str
    fecha_inicio: date
    fecha_fin: date
    dias_solicitados: int
    motivo: str
    estado: str
    adjunto_url: Optional[str]
    comentario_evaluador: Optional[str]
    evaluado_por_id: Optional[int]
    fecha_evaluacion: Optional[datetime]
    fecha_creacion: datetime