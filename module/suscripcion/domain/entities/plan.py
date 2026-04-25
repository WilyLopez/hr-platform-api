from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from shared.constants import PlanesNombre


@dataclass
class Plan:
    id: Optional[int]
    nombre: str
    precio_mensual: float
    limite_usuarios: int
    almacenamiento_gb: int
    es_activo: bool
    fecha_creacion: datetime
    fecha_actualizacion: Optional[datetime]

    def __post_init__(self):
        if self.precio_mensual < 0:
            raise ValueError("El precio mensual no puede ser negativo.")
        if self.limite_usuarios < 1:
            raise ValueError("El límite de usuarios debe ser al menos 1.")
        if self.almacenamiento_gb < 1:
            raise ValueError("El almacenamiento debe ser al menos 1 GB.")

    def es_basico(self) -> bool:
        return self.nombre == PlanesNombre.BASICO

    def es_pro(self) -> bool:
        return self.nombre == PlanesNombre.PRO

    def actualizar(
        self,
        precio_mensual: float,
        limite_usuarios: int,
        almacenamiento_gb: int,
    ) -> None:
        self.precio_mensual = precio_mensual
        self.limite_usuarios = limite_usuarios
        self.almacenamiento_gb = almacenamiento_gb
        self.fecha_actualizacion = datetime.now()

    def desactivar(self) -> None:
        self.es_activo = False