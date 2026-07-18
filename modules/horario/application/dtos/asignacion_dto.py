from dataclasses import dataclass
from typing import Optional
from datetime import date, datetime

@dataclass
class AsignarHorarioInputDTO:
    empresa_id: int
    empleado_id: int
    horario_id: int
    fecha_desde: date
    creado_por_id: int
    fecha_hasta: Optional[date] = None

@dataclass
class AsignacionOutputDTO:
    id: int
    empleado_id: int
    horario_id: int
    horario_nombre: str
    fecha_desde: date
    fecha_hasta: Optional[date]
    fecha_creacion: datetime
