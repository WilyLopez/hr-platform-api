from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class MarcajeRegistradoEvent:
    registro_id: int
    empresa_id: int
    empleado_id: int
    sede_id: int
    tipo: str
    metodo: str
    es_tardanza: bool
    timestamp: datetime


@dataclass(frozen=True)
class MarcajeRechazadoEvent:
    empresa_id: int
    empleado_id: int
    razon: str
    timestamp: datetime