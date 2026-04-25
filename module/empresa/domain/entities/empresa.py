from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from shared.domain.value_objects import Email, Ruc
from shared.constants import EstadosEmpresa


@dataclass
class Empresa:
    id: Optional[int]
    ruc: Ruc
    razon_social: str
    nombre_comercial: str
    correo: Email
    telefono: str
    direccion: str
    logo_url: Optional[str]
    estado: str
    fecha_registro: datetime
    fecha_actualizacion: Optional[datetime]

    def __post_init__(self):
        if not self.razon_social.strip():
            raise ValueError("La razón social no puede estar vacía.")
        if not self.telefono.strip():
            raise ValueError("El teléfono no puede estar vacío.")

    def activar(self) -> None:
        self.estado = EstadosEmpresa.ACTIVA

    def suspender(self) -> None:
        self.estado = EstadosEmpresa.SUSPENDIDA

    def marcar_en_prueba(self) -> None:
        self.estado = EstadosEmpresa.EN_PRUEBA

    def eliminar(self) -> None:
        self.estado = EstadosEmpresa.ELIMINADA

    def esta_activa(self) -> bool:
        return self.estado in {EstadosEmpresa.ACTIVA, EstadosEmpresa.EN_PRUEBA}

    def esta_suspendida(self) -> bool:
        return self.estado == EstadosEmpresa.SUSPENDIDA

    def actualizar_perfil(
        self,
        nombre_comercial: str,
        telefono: str,
        direccion: str,
        logo_url: Optional[str] = None,
    ) -> None:
        self.nombre_comercial = nombre_comercial
        self.telefono = telefono
        self.direccion = direccion
        self.logo_url = logo_url
        self.fecha_actualizacion = datetime.now()