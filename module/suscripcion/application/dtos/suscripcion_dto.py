from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class CambiarPlanInputDTO:
    empresa_id: int
    nuevo_plan_id: int


@dataclass
class SuscripcionOutputDTO:
    id: int
    empresa_id: int
    plan_id: int
    plan_nombre: str
    estado: str
    fecha_inicio: datetime
    fecha_fin_trial: Optional[datetime]
    fecha_proxima_facturacion: Optional[datetime]
    usuarios_activos: int
    limite_usuarios: int
    dias_restantes_trial: Optional[int]