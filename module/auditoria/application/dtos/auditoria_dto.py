from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any


@dataclass
class RegistrarEventoInputDTO:
    empresa_id: Optional[int]
    usuario_id: Optional[int]
    rol_usuario: Optional[str]
    tipo_evento: str
    descripcion: str
    ip_address: Optional[str]
    detalles: Dict[str, Any]


@dataclass
class ConsultarAuditoriaInputDTO:
    empresa_id: Optional[int]
    usuario_id: Optional[int]
    rol: Optional[str]
    tipo_evento: Optional[str]
    fecha_desde: Optional[datetime]
    fecha_hasta: Optional[datetime]
    page: int = 1
    page_size: int = 20


@dataclass
class ExportarAuditoriaInputDTO:
    empresa_id: Optional[int]
    fecha_desde: datetime
    fecha_hasta: datetime
    formato: str


@dataclass
class RegistroAuditoriaOutputDTO:
    id: int
    empresa_id: Optional[int]
    usuario_id: Optional[int]
    rol_usuario: Optional[str]
    tipo_evento: str
    descripcion: str
    ip_address: Optional[str]
    detalles: Dict[str, Any]
    timestamp: datetime