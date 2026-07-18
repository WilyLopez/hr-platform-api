from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional, List


@dataclass
class RegistrarMarcajeInputDTO:
    usuario_id: int
    empresa_id: int
    origen: str
    token_qr: Optional[str] = None
    latitud: Optional[float] = None
    longitud: Optional[float] = None


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
    solo_extras: bool = False
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
    origen: str
    estado_auditoria: str
    resultado: str
    minutos_tardanza: int
    minutos_extra: int
    minutos_temprano: int
    horas_trabajadas: float
    timestamp: datetime
    estado_extras: Optional[str] = None
    minutos_extra_aprobados: Optional[int] = None


@dataclass
class ReporteAsistenciaOutputDTO:
    empleado_id: int
    empleado_nombre: str
    total_dias: int
    dias_presentes: int
    dias_ausentes: int
    tardanzas: int
    registros: List[RegistroAsistenciaOutputDTO]


@dataclass
class EstadoAsistenciaHoyDTO:
    estado_actual: str  # SIN_MARCAR, TRABAJANDO, EN_REFRIGERIO, FINALIZADO
    horario_hoy: str  # "09:00 - 18:00" o "Día Libre"
    ultimo_marcaje: Optional[str]  # Ej: "Entrada 08:57"
    tiempo_trabajado_str: str  # Ej: "03h 25m"
    tiempo_trabajado_minutos: int