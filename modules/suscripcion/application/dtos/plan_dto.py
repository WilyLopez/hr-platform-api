from dataclasses import dataclass
from typing import Optional


@dataclass
class CrearPlanInputDTO:
    nombre: str
    precio_mensual: float
    limite_usuarios: int
    almacenamiento_gb: int
    color: str = "#3b82f6"
    descripcion_corta: Optional[str] = None
    orden: int = 0
    es_activo: bool = True


@dataclass
class ActualizarPlanInputDTO:
    plan_id: int
    precio_mensual: float
    limite_usuarios: int
    almacenamiento_gb: int
    color: str
    descripcion_corta: Optional[str]
    orden: int
    es_activo: bool


@dataclass
class PlanOutputDTO:
    id: int
    nombre: str
    precio_mensual: float
    limite_usuarios: int
    almacenamiento_gb: int
    color: str
    descripcion_corta: Optional[str]
    orden: int
    es_activo: bool