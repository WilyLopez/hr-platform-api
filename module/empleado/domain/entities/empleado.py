from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from shared.domain.value_objects import Email, CodigoUnico, NumeroDocumento
from shared.constants import EstadosEmpleado
from modules.empleado.domain.exceptions import (
    EmpleadoInactivoException,
    ModificacionCodigoUnicoException,
)


@dataclass
class Empleado:
    id: Optional[int]
    empresa_id: int
    usuario_id: Optional[int]
    codigo_unico: CodigoUnico
    nombres: str
    apellidos: str
    documento: NumeroDocumento
    correo: Email
    cargo: str
    area: str
    sede_id: int
    estado: str
    fecha_ingreso: datetime
    fecha_creacion: datetime
    fecha_actualizacion: Optional[datetime]

    def nombre_completo(self) -> str:
        return f"{self.nombres} {self.apellidos}"

    def esta_activo(self) -> bool:
        return self.estado == EstadosEmpleado.ACTIVO

    def verificar_esta_activo(self) -> None:
        if not self.esta_activo():
            raise EmpleadoInactivoException()

    def desactivar(self) -> None:
        self.estado = EstadosEmpleado.INACTIVO
        self.fecha_actualizacion = datetime.now()

    def reactivar(self) -> None:
        self.estado = EstadosEmpleado.ACTIVO
        self.fecha_actualizacion = datetime.now()

    def actualizar(
        self,
        nombres: str,
        apellidos: str,
        correo: Email,
        cargo: str,
        area: str,
    ) -> None:
        self.nombres = nombres
        self.apellidos = apellidos
        self.correo = correo
        self.cargo = cargo
        self.area = area
        self.fecha_actualizacion = datetime.now()

    def asignar_sede(self, sede_id: int) -> None:
        self.sede_id = sede_id
        self.fecha_actualizacion = datetime.now()