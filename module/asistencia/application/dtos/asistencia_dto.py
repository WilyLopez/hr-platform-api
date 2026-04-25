from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional, List


@dataclass
class RegistrarMarcajeInputDTO:
    empleado_id: int
    empresa_id: int
    token_qr: str
    latitud: float
    longitud: float


@dataclass
class RegistrarManualInputDTO:
    empleado_id: int
    empresa_id: int
    admin_id: int
    tipo: str
    fecha: date
    hora: str
    justificacion: str


@dataclass
class ListarAsistenciaInputDTO:
    empresa_id: int
    empleado_id: Optional[int] = None
    sede_id: Optional[int] = None
    area: Optional[str] = None
    fecha_desde: Optional[date] = None
    fecha_hasta: Optional[date] = None
    page: int = 1
    page_size: int = 20


@dataclass
class RegistroAsistenciaOutputDTO:
    id: int
    empleado_id: int
    empleado_nombre: str
    sede_id: int
    sede_nombre: str
    tipo: str
    metodo: str
    es_tardanza: bool
    es_manual: bool
    timestamp: datetime


@dataclass
class ReporteAsistenciaOutputDTO:
    empleado_id: int
    empleado_nombre: str
    total_dias: int
    dias_presentes: int
    dias_ausentes: int
    tardanzas: int
    registros: List[RegistroAsistenciaOutputDTO]