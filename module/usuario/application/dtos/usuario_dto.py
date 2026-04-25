from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class CrearUsuarioInputDTO:
    empresa_id: Optional[int]
    rol_nombre: str
    correo: str
    contrasena: str


@dataclass
class ActualizarUsuarioInputDTO:
    usuario_id: int
    empresa_id: Optional[int]
    correo: str


@dataclass
class CambiarContrasenaInputDTO:
    usuario_id: int
    contrasena_actual: str
    contrasena_nueva: str


@dataclass
class RecuperarContrasenaInputDTO:
    correo: str


@dataclass
class UsuarioOutputDTO:
    id: int
    empresa_id: Optional[int]
    codigo_unico: str
    correo: str
    rol: str
    estado: str
    ultimo_acceso: Optional[datetime]
    fecha_creacion: datetime