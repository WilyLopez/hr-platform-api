from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class TrialActivadoEvent:
    suscripcion_id: int
    empresa_id: int
    fecha_fin_trial: datetime
    timestamp: datetime


@dataclass(frozen=True)
class TrialPorVencerEvent:
    suscripcion_id: int
    empresa_id: int
    correo_propietario: str
    dias_restantes: int
    timestamp: datetime


@dataclass(frozen=True)
class SuscripcionActivadaEvent:
    suscripcion_id: int
    empresa_id: int
    plan_nombre: str
    timestamp: datetime


@dataclass(frozen=True)
class SuscripcionSuspendidaEvent:
    suscripcion_id: int
    empresa_id: int
    correo_propietario: str
    timestamp: datetime