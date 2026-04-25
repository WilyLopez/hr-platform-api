from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class EmpresaRegistradaEvent:
    empresa_id: int
    ruc: str
    correo: str
    plan_nombre: str
    timestamp: datetime


@dataclass(frozen=True)
class EmpresaSuspendidaEvent:
    empresa_id: int
    suspendido_por_id: int
    razon: str
    timestamp: datetime


@dataclass(frozen=True)
class EmpresaEliminadaEvent:
    empresa_id: int
    eliminado_por_id: int
    timestamp: datetime