from datetime import datetime
from shared.application.base_use_case import BaseUseCase
from modules.suscripcion.domain.repositories.plan_repository import PlanRepository
from modules.suscripcion.application.dtos.plan_dto import ActualizarPlanInputDTO, PlanOutputDTO
from shared.domain.exceptions import EntityNotFoundException, BusinessRuleViolationException

class PrecioPlanInmutableException(BusinessRuleViolationException):
    def __init__(self):
        super().__init__(
            message="No se puede cambiar el precio de un plan que ya tiene empresas suscritas. Por favor, crea una nueva versión del plan.",
            code="precio_plan_inmutable",
        )


class ActualizarPlanUseCase(BaseUseCase[ActualizarPlanInputDTO, PlanOutputDTO]):
    def __init__(self, plan_repository: PlanRepository, suscripcion_repository):
        self._plan_repository = plan_repository
        self._suscripcion_repository = suscripcion_repository

    def execute(self, input_dto: ActualizarPlanInputDTO) -> PlanOutputDTO:
        plan = self._plan_repository.get_by_id(input_dto.plan_id)
        if not plan:
            raise EntityNotFoundException("Plan", str(input_dto.plan_id))

        # Verificar inmutabilidad del precio
        if float(plan.precio_mensual) != float(input_dto.precio_mensual):
            uso_count = self._suscripcion_repository.count_by_plan(plan.id)
            if uso_count > 0:
                raise PrecioPlanInmutableException()

        # Actualizar campos
        plan.precio_mensual = input_dto.precio_mensual
        plan.limite_usuarios = input_dto.limite_usuarios
        plan.almacenamiento_gb = input_dto.almacenamiento_gb
        plan.color = input_dto.color
        plan.descripcion_corta = input_dto.descripcion_corta
        plan.orden = input_dto.orden
        plan.es_activo = input_dto.es_activo
        plan.fecha_actualizacion = datetime.now()

        plan = self._plan_repository.save(plan)

        return PlanOutputDTO(
            id=plan.id,
            nombre=plan.nombre,
            precio_mensual=plan.precio_mensual,
            limite_usuarios=plan.limite_usuarios,
            almacenamiento_gb=plan.almacenamiento_gb,
            color=plan.color,
            descripcion_corta=plan.descripcion_corta,
            orden=plan.orden,
            es_activo=plan.es_activo,
        )
