from typing import Optional, List
from datetime import datetime, timedelta
from modules.suscripcion.domain.entities.suscripcion import Suscripcion
from modules.suscripcion.domain.repositories.suscripcion_repository import SuscripcionRepository
from modules.suscripcion.infrastructure.models.suscripcion_model import SuscripcionModel
from shared.constants import EstadosSuscripcion, TRIAL_ALERT_DAYS_BEFORE


class DjangoSuscripcionRepository(SuscripcionRepository):
    def get_by_id(self, id: int) -> Optional[Suscripcion]:
        try:
            return self._to_entity(SuscripcionModel.objects.get(pk=id))
        except SuscripcionModel.DoesNotExist:
            return None

    def get_by_empresa(self, empresa_id: int) -> Optional[Suscripcion]:
        try:
            return self._to_entity(SuscripcionModel.objects.get(empresa_id=empresa_id))
        except SuscripcionModel.DoesNotExist:
            return None

    def get_trials_por_vencer(self, dias: int) -> List[Suscripcion]:
        limite = datetime.now() + timedelta(days=dias)
        qs = SuscripcionModel.objects.filter(
            estado=EstadosSuscripcion.TRIAL,
            fecha_fin_trial__lte=limite,
            fecha_fin_trial__gte=datetime.now(),
        )
        return [self._to_entity(m) for m in qs]

    def get_vencidas_sin_pago(self, dias_gracia: int) -> List[Suscripcion]:
        limite = datetime.now() - timedelta(days=dias_gracia)
        qs = SuscripcionModel.objects.filter(
            estado=EstadosSuscripcion.ACTIVA,
            fecha_proxima_facturacion__lt=limite,
        )
        return [self._to_entity(m) for m in qs]

    def save(self, suscripcion: Suscripcion) -> Suscripcion:
        if suscripcion.id:
            model = SuscripcionModel.objects.get(pk=suscripcion.id)
        else:
            model = SuscripcionModel()

        model.empresa_id = suscripcion.empresa_id
        model.plan_id = suscripcion.plan_id
        model.estado = suscripcion.estado
        model.fecha_inicio = suscripcion.fecha_inicio
        model.fecha_fin_trial = suscripcion.fecha_fin_trial
        model.fecha_proxima_facturacion = suscripcion.fecha_proxima_facturacion
        model.usuarios_activos = suscripcion.usuarios_activos
        model.fecha_actualizacion = suscripcion.fecha_actualizacion
        model.save()

        suscripcion.id = model.pk
        return suscripcion

    def exists_by_empresa(self, empresa_id: int) -> bool:
        return SuscripcionModel.objects.filter(empresa_id=empresa_id).exists()

    def _to_entity(self, model: SuscripcionModel) -> Suscripcion:
        from modules.usuario.infrastructure.models.usuario_model import UsuarioModel
        from shared.constants import EstadosUsuario

        usuarios_activos = UsuarioModel.objects.filter(
            empresa_id=model.empresa_id,
            estado=EstadosUsuario.ACTIVO
        ).count()

        return Suscripcion(
            id=model.pk,
            empresa_id=model.empresa_id,
            plan_id=model.plan_id,
            plan_nombre=model.plan.nombre,
            plan_limite_usuarios=model.plan.limite_usuarios,
            estado=model.estado,
            fecha_inicio=model.fecha_inicio,
            fecha_fin_trial=model.fecha_fin_trial,
            fecha_proxima_facturacion=model.fecha_proxima_facturacion,
            usuarios_activos=usuarios_activos,
            fecha_creacion=model.fecha_creacion,
            fecha_actualizacion=model.fecha_actualizacion,
        )