from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class TipoPermiso:
    id: Optional[int]
    empresa_id: int
    nombre: str
    descripcion: str
    requiere_adjunto: bool
    es_activo: bool
    fecha_creacion: datetime
    fecha_actualizacion: Optional[datetime]

    def __post_init__(self):
        if not self.nombre.strip():
            raise ValueError("El nombre del tipo de permiso no puede estar vacío.")

    def actualizar(self, nombre: str, descripcion: str, requiere_adjunto: bool) -> None:
        self.nombre = nombre
        self.descripcion = descripcion
        self.requiere_adjunto = requiere_adjunto
        self.fecha_actualizacion = datetime.now()

    def desactivar(self) -> None:
        self.es_activo = False