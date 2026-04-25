from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from shared.domain.value_objects import Email, CodigoUnico
from shared.constants import EstadosUsuario, MAX_LOGIN_ATTEMPTS
from modules.usuario.domain.exceptions import (
    UsuarioBloqueadoException,
    UsuarioInactivoException,
    MaximosIntentosAlcanzadosException,
)


@dataclass
class Usuario:
    id: Optional[int]
    empresa_id: Optional[int]
    rol_id: int
    codigo_unico: CodigoUnico
    correo: Email
    password_hash: str
    estado: str
    intentos_fallidos: int
    ultimo_acceso: Optional[datetime]
    fecha_creacion: datetime
    fecha_actualizacion: Optional[datetime]

    def verificar_puede_autenticarse(self) -> None:
        if self.estado == EstadosUsuario.BLOQUEADO:
            raise UsuarioBloqueadoException()
        if self.estado == EstadosUsuario.INACTIVO:
            raise UsuarioInactivoException()

    def registrar_intento_fallido(self, max_intentos: int = MAX_LOGIN_ATTEMPTS) -> None:
        self.intentos_fallidos += 1
        if self.intentos_fallidos >= max_intentos:
            self.estado = EstadosUsuario.BLOQUEADO
            raise MaximosIntentosAlcanzadosException(max_intentos)

    def registrar_acceso_exitoso(self) -> None:
        self.intentos_fallidos = 0
        self.ultimo_acceso = datetime.now()

    def desbloquear(self) -> None:
        self.estado = EstadosUsuario.ACTIVO
        self.intentos_fallidos = 0

    def desactivar(self) -> None:
        self.estado = EstadosUsuario.INACTIVO

    def activar(self) -> None:
        self.estado = EstadosUsuario.ACTIVO

    def esta_activo(self) -> bool:
        return self.estado == EstadosUsuario.ACTIVO

    def cambiar_password(self, nuevo_hash: str) -> None:
        self.password_hash = nuevo_hash
        self.fecha_actualizacion = datetime.now()