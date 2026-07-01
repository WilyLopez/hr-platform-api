from django.utils import timezone
from shared.application.base_use_case import BaseUseCase
from modules.suscripcion.domain.repositories.suscripcion_repository import SuscripcionRepository
from modules.suscripcion.domain.exceptions import SuscripcionNoEncontradaException
from modules.suscripcion.application.dtos.suscripcion_dto import SuscripcionOutputDTO


class ObtenerEstadoSuscripcionUseCase(BaseUseCase[int, SuscripcionOutputDTO]):
    def __init__(self, suscripcion_repository: SuscripcionRepository):
        self._suscripcion_repository = suscripcion_repository

    def execute(self, empresa_id: int) -> SuscripcionOutputDTO:
        suscripcion = self._suscripcion_repository.get_by_empresa(empresa_id)
        if not suscripcion:
            raise SuscripcionNoEncontradaException(str(empresa_id))

        dias_restantes = None
        if suscripcion.fecha_fin_trial:
            dias_restantes = max(0, (suscripcion.fecha_fin_trial - timezone.now()).days)

        return SuscripcionOutputDTO(
            id=suscripcion.id,
            empresa_id=suscripcion.empresa_id,
            plan_id=suscripcion.plan_id,
            plan_nombre=suscripcion.plan_nombre,
            estado=suscripcion.estado,
            fecha_inicio=suscripcion.fecha_inicio,
            fecha_fin_trial=suscripcion.fecha_fin_trial,
            fecha_proxima_facturacion=suscripcion.fecha_proxima_facturacion,
            usuarios_activos=suscripcion.usuarios_activos,
            limite_usuarios=suscripcion.plan_limite_usuarios,
            dias_restantes_trial=dias_restantes,
        )