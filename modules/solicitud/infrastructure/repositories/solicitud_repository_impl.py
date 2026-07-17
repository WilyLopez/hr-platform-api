from typing import Optional, List
from datetime import date
from modules.solicitud.domain.entities.solicitud import Solicitud
from modules.solicitud.domain.repositories.solicitud_repository import SolicitudRepository
from modules.solicitud.infrastructure.models.solicitud_model import SolicitudModel
from shared.constants import EstadosSolicitud


class DjangoSolicitudRepository(SolicitudRepository):
    def get_by_id(self, id: int) -> Optional[Solicitud]:
        try:
            return self._to_entity(SolicitudModel.objects.get(pk=id))
        except SolicitudModel.DoesNotExist:
            return None

    def get_by_empleado(
        self,
        empleado_id: int,
        estado: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> List[Solicitud]:
        qs = SolicitudModel.objects.filter(empleado_id=empleado_id)
        if estado:
            qs = qs.filter(estado=estado)
        offset = (page - 1) * page_size
        return [self._to_entity(m) for m in qs.order_by("-fecha_creacion")[offset: offset + page_size]]

    def get_by_empresa(
        self,
        empresa_id: int,
        estado: Optional[str] = None,
        empleado_id: Optional[int] = None,
        tipo_permiso_id: Optional[int] = None,
        fecha_desde: Optional[date] = None,
        fecha_hasta: Optional[date] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> List[Solicitud]:
        qs = SolicitudModel.objects.filter(empresa_id=empresa_id)
        if estado:
            qs = qs.filter(estado=estado)
        if empleado_id:
            qs = qs.filter(empleado_id=empleado_id)
        if tipo_permiso_id:
            qs = qs.filter(tipo_permiso_id=tipo_permiso_id)
        if fecha_desde:
            qs = qs.filter(fecha_inicio__gte=fecha_desde)
        if fecha_hasta:
            qs = qs.filter(fecha_fin__lte=fecha_hasta)
        offset = (page - 1) * page_size
        return [self._to_entity(m) for m in qs.order_by("-fecha_creacion")[offset: offset + page_size]]

    def get_aprobadas_en_periodo(
        self, empleado_id: int, fecha_desde: date, fecha_hasta: date
    ) -> List[Solicitud]:
        qs = SolicitudModel.objects.filter(
            empleado_id=empleado_id,
            estado=EstadosSolicitud.APROBADA,
            fecha_inicio__lte=fecha_hasta,
            fecha_fin__gte=fecha_desde,
        )
        return [self._to_entity(m) for m in qs]

    def save(self, solicitud: Solicitud) -> Solicitud:
        if solicitud.id:
            model = SolicitudModel.objects.get(pk=solicitud.id)
        else:
            model = SolicitudModel()

        model.empresa_id = solicitud.empresa_id
        model.empleado_id = solicitud.empleado_id
        model.tipo_permiso_id = solicitud.tipo_permiso_id
        model.tipo_permiso_nombre = solicitud.tipo_permiso_nombre
        model.fecha_inicio = solicitud.fecha_inicio
        model.fecha_fin = solicitud.fecha_fin
        model.hora_inicio = solicitud.hora_inicio
        model.hora_fin = solicitud.hora_fin
        model.motivo = solicitud.motivo
        model.estado = solicitud.estado
        model.adjunto_url = solicitud.adjunto_url
        model.comentario_evaluador = solicitud.comentario_evaluador
        model.evaluado_por_id = solicitud.evaluado_por_id
        model.fecha_evaluacion = solicitud.fecha_evaluacion
        model.fecha_actualizacion = solicitud.fecha_actualizacion
        model.save()

        solicitud.id = model.pk
        return solicitud

    def count_by_empresa(self, empresa_id: int, estado: Optional[str] = None) -> int:
        qs = SolicitudModel.objects.filter(empresa_id=empresa_id)
        if estado:
            qs = qs.filter(estado=estado)
        return qs.count()

    def _to_entity(self, model: SolicitudModel) -> Solicitud:
        return Solicitud(
            id=model.pk,
            empresa_id=model.empresa_id,
            empleado_id=model.empleado_id,
            tipo_permiso_id=model.tipo_permiso_id,
            tipo_permiso_nombre=model.tipo_permiso_nombre,
            fecha_inicio=model.fecha_inicio,
            fecha_fin=model.fecha_fin,
            hora_inicio=model.hora_inicio,
            hora_fin=model.hora_fin,
            motivo=model.motivo,
            estado=model.estado,
            adjunto_url=model.adjunto_url,
            comentario_evaluador=model.comentario_evaluador,
            evaluado_por_id=model.evaluado_por_id,
            fecha_evaluacion=model.fecha_evaluacion,
            fecha_creacion=model.fecha_creacion,
            fecha_actualizacion=model.fecha_actualizacion,
        )