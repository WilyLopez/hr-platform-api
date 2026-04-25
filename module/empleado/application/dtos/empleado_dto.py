from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional


@dataclass
class RegistrarEmpleadoInputDTO:
    empresa_id: int
    nombres: str
    apellidos: str
    tipo_documento: str
    numero_documento: str
    correo: str
    cargo: str
    area: str
    sede_id: int
    fecha_ingreso: date


@dataclass
class ActualizarEmpleadoInputDTO:
    empleado_id: int
    empresa_id: int
    nombres: str
    apellidos: str
    correo: str
    cargo: str
    area: str


@dataclass
class AsignarSedeInputDTO:
    empleado_id: int
    empresa_id: int
    sede_id: int


@dataclass
class ListarEmpleadosInputDTO:
    empresa_id: int
    estado: Optional[str] = None
    area: Optional[str] = None
    sede_id: Optional[int] = None
    search: Optional[str] = None
    page: int = 1
    page_size: int = 20


@dataclass
class EmpleadoOutputDTO:
    id: int
    empresa_id: int
    codigo_unico: str
    nombres: str
    apellidos: str
    tipo_documento: str
    numero_documento: str
    correo: str
    cargo: str
    area: str
    sede_id: int
    sede_nombre: Optional[str]
    estado: str
    fecha_ingreso: date
    fecha_creacion: datetime