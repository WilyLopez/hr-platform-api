from datetime import timedelta
from django.utils import timezone
from shared.application.base_use_case import BaseUseCase
from modules.suscripcion.domain.repositories.suscripcion_repository import SuscripcionRepository
from modules.suscripcion.domain.repositories.plan_repository import PlanRepository
from modules.suscripcion.domain.exceptions import (
    SuscripcionNoEncontradaException,
    PlanNoEncontradoException,
    CambioPlanNoValidoException,
)
from modules.suscripcion.application.dtos.suscripcion_dto import CambiarPlanInputDTO, SuscripcionOutputDTO


class CambiarPlanUseCase(BaseUseCase[CambiarPlanInputDTO, SuscripcionOutputDTO]):
    def __init__(
        self,
        suscripcion_repository: SuscripcionRepository,
        plan_repository: PlanRepository,
    ):
        self._suscripcion_repository = suscripcion_repository
        self._plan_repository = plan_repository

    def execute(self, input_dto: CambiarPlanInputDTO) -> SuscripcionOutputDTO:
        suscripcion = self._suscripcion_repository.get_by_empresa(input_dto.empresa_id)
        if not suscripcion:
            raise SuscripcionNoEncontradaException(str(input_dto.empresa_id))

        nuevo_plan = self._plan_repository.get_by_id(input_dto.nuevo_plan_id)
        if not nuevo_plan:
            raise PlanNoEncontradoException(str(input_dto.nuevo_plan_id))

        if suscripcion.usuarios_activos > nuevo_plan.limite_usuarios:
            raise CambioPlanNoValidoException(
                suscripcion.plan_nombre,
                nuevo_plan.nombre,
                f"tiene {suscripcion.usuarios_activos} usuarios activos y el nuevo plan admite {nuevo_plan.limite_usuarios}.",
            )

        suscripcion.plan_id = nuevo_plan.id
        suscripcion.plan_nombre = nuevo_plan.nombre
        suscripcion.plan_limite_usuarios = nuevo_plan.limite_usuarios
        suscripcion.estado = "ACTIVA"
        suscripcion.fecha_proxima_facturacion = timezone.now() + timedelta(days=30)
        suscripcion.fecha_actualizacion = timezone.now()

        suscripcion = self._suscripcion_repository.save(suscripcion)
        dias_restantes = None
        if suscripcion.fecha_fin_trial:
            dias_restantes = (suscripcion.fecha_fin_trial - timezone.now()).days

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