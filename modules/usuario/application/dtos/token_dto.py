from dataclasses import dataclass
from typing import Optional


@dataclass
class AutenticarUsuarioInputDTO:
    codigo_unico: str
    contrasena: str
    ip_address: str


@dataclass
class TokenSecurityDTO:
    must_change_password: bool


@dataclass
class TokenOutputDTO:
    access: str
    refresh: str
    usuario_id: int
    codigo_unico: str
    empresa_id: Optional[int]
    rol: str
    security: TokenSecurityDTO


@dataclass
class RefrescarTokenInputDTO:
    refresh: str


@dataclass
class RefrescarTokenOutputDTO:
    access: str