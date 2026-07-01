from typing import Optional, List
from modules.suscripcion.domain.entities.plan import Plan
from modules.suscripcion.domain.repositories.plan_repository import PlanRepository
from modules.suscripcion.infrastructure.models.plan_model import PlanModel


class DjangoPlanRepository(PlanRepository):
    def get_by_id(self, id: int) -> Optional[Plan]:
        try:
            return self._to_entity(PlanModel.objects.get(pk=id))
        except PlanModel.DoesNotExist:
            return None

    def get_by_nombre(self, nombre: str) -> Optional[Plan]:
        try:
            return self._to_entity(PlanModel.objects.get(nombre=nombre))
        except PlanModel.DoesNotExist:
            return None

    def get_all_activos(self) -> List[Plan]:
        return [self._to_entity(m) for m in PlanModel.objects.filter(es_activo=True)]

    def save(self, plan: Plan) -> Plan:
        if plan.id:
            model = PlanModel.objects.get(pk=plan.id)
        else:
            model = PlanModel()

        model.nombre = plan.nombre
        model.precio_mensual = plan.precio_mensual
        model.limite_usuarios = plan.limite_usuarios
        model.almacenamiento_gb = plan.almacenamiento_gb
        model.color = plan.color
        model.descripcion_corta = plan.descripcion_corta
        model.orden = plan.orden
        model.es_activo = plan.es_activo
        model.fecha_actualizacion = plan.fecha_actualizacion
        model.save()

        plan.id = model.pk
        return plan

    def exists(self, id: int) -> bool:
        return PlanModel.objects.filter(pk=id).exists()

    def _to_entity(self, model: PlanModel) -> Plan:
        return Plan(
            id=model.pk,
            nombre=model.nombre,
            precio_mensual=float(model.precio_mensual),
            limite_usuarios=model.limite_usuarios,
            almacenamiento_gb=model.almacenamiento_gb,
            color=model.color,
            descripcion_corta=model.descripcion_corta,
            orden=model.orden,
            es_activo=model.es_activo,
            fecha_creacion=model.fecha_creacion,
            fecha_actualizacion=model.fecha_actualizacion,
        )