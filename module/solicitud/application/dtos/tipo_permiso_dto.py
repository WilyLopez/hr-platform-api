from dataclasses import dataclass


@dataclass
class CrearTipoPermisoInputDTO:
    empresa_id: int
    nombre: str
    descripcion: str
    requiere_adjunto: bool


@dataclass
class ActualizarTipoPermisoInputDTO:
    tipo_permiso_id: int
    empresa_id: int
    nombre: str
    descripcion: str
    requiere_adjunto: bool


@dataclass
class TipoPermisoOutputDTO:
    id: int
    empresa_id: int
    nombre: str
    descripcion: str
    requiere_adjunto: bool
    es_activo: bool