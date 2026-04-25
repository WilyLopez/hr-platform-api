from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class EmpleadoCreadoEvent:
    empleado_id: int
    empresa_id: int
    codigo_unico: str
    correo: str
    timestamp: datetime


@dataclass(frozen=True)
class EmpleadoDesactivadoEvent:
    empleado_id: int
    empresa_id: int
    desactivado_por_id: int
    timestamp: datetime