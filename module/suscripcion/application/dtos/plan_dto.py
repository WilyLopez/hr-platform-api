from dataclasses import dataclass
from typing import Optional


@dataclass
class CrearPlanInputDTO:
    nombre: str
    precio_mensual: float
    limite_usuarios: int
    almacenamiento_gb: int


@dataclass
class ActualizarPlanInputDTO:
    plan_id: int
    precio_mensual: float
    limite_usuarios: int
    almacenamiento_gb: int


@dataclass
class PlanOutputDTO:
    id: int
    nombre: str
    precio_mensual: float
    limite_usuarios: int
    almacenamiento_gb: int
    es_activo: bool