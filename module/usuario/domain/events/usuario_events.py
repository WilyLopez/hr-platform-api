from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class UsuarioCreadoEvent:
    usuario_id: int
    empresa_id: Optional[int]
    codigo_unico: str
    correo: str
    rol: str
    timestamp: datetime


@dataclass(frozen=True)
class InicioSesionExitosoEvent:
    usuario_id: int
    empresa_id: Optional[int]
    ip_address: str
    timestamp: datetime


@dataclass(frozen=True)
class IntentoFallidoEvent:
    usuario_id: int
    ip_address: str
    intentos_acumulados: int
    timestamp: datetime


@dataclass(frozen=True)
class UsuarioBloqueadoEvent:
    usuario_id: int
    empresa_id: Optional[int]
    timestamp: datetime