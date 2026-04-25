from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional
from shared.constants import EstadosSuscripcion, TRIAL_PERIOD_DAYS, TRIAL_ALERT_DAYS_BEFORE
from modules.suscripcion.domain.exceptions import (
    SuscripcionVencidaException,
    SuscripcionSuspendidaException,
    LimiteUsuariosAlcanzadoException,
)


@dataclass
class Suscripcion:
    id: Optional[int]
    empresa_id: int
    plan_id: int
    plan_nombre: str
    plan_limite_usuarios: int
    estado: str
    fecha_inicio: datetime
    fecha_fin_trial: Optional[datetime]
    fecha_proxima_facturacion: Optional[datetime]
    usuarios_activos: int
    fecha_creacion: datetime
    fecha_actualizacion: Optional[datetime]

    def verificar_puede_operar(self) -> None:
        if self.estado == EstadosSuscripcion.VENCIDA:
            raise SuscripcionVencidaException()
        if self.estado == EstadosSuscripcion.SUSPENDIDA:
            raise SuscripcionSuspendidaException()

    def verificar_limite_usuarios(self) -> None:
        if self.usuarios_activos >= self.plan_limite_usuarios:
            raise LimiteUsuariosAlcanzadoException(self.plan_nombre, self.plan_limite_usuarios)

    def activar_trial(self) -> None:
        self.estado = EstadosSuscripcion.TRIAL
        self.fecha_fin_trial = self.fecha_inicio + timedelta(days=TRIAL_PERIOD_DAYS)

    def activar(self, fecha_proxima_facturacion: datetime) -> None:
        self.estado = EstadosSuscripcion.ACTIVA
        self.fecha_proxima_facturacion = fecha_proxima_facturacion

    def suspender(self) -> None:
        self.estado = EstadosSuscripcion.SUSPENDIDA

    def vencer(self) -> None:
        self.estado = EstadosSuscripcion.VENCIDA

    def esta_en_trial(self) -> bool:
        return self.estado == EstadosSuscripcion.TRIAL

    def trial_por_vencer(self) -> bool:
        if not self.esta_en_trial() or self.fecha_fin_trial is None:
            return False
        dias_restantes = (self.fecha_fin_trial - datetime.now()).days
        return 0 <= dias_restantes <= TRIAL_ALERT_DAYS_BEFORE

    def incrementar_usuarios(self) -> None:
        self.usuarios_activos += 1

    def decrementar_usuarios(self) -> None:
        if self.usuarios_activos > 0:
            self.usuarios_activos -= 1