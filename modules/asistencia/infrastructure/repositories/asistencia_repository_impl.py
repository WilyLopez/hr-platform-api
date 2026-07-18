from typing import Optional, List
from datetime import date, datetime
from shared.domain.value_objects import Coordenadas
from modules.asistencia.domain.entities.registro_asistencia import RegistroAsistencia
from modules.asistencia.domain.repositories.asistencia_repository import AsistenciaRepository
from modules.asistencia.infrastructure.models.asistencia_model import RegistroAsistenciaModel


class DjangoAsistenciaRepository(AsistenciaRepository):
    def get_by_id(self, id: int) -> Optional[RegistroAsistencia]:
        try:
            return self._to_entity(RegistroAsistenciaModel.objects.get(pk=id))
        except RegistroAsistenciaModel.DoesNotExist:
            return None

    def get_by_empleado(
        self,
        empleado_id: int,
        fecha_desde: Optional[date] = None,
        fecha_hasta: Optional[date] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> List[RegistroAsistencia]:
        qs = RegistroAsistenciaModel.objects.filter(empleado_id=empleado_id)
        if fecha_desde:
            qs = qs.filter(timestamp__date__gte=fecha_desde)
        if fecha_hasta:
            qs = qs.filter(timestamp__date__lte=fecha_hasta)
        offset = (page - 1) * page_size
        return [self._to_entity(m) for m in qs.order_by("timestamp")[offset: offset + page_size]]

    def get_marcajes_del_dia(self, empleado_id: int, fecha: date) -> List[RegistroAsistencia]:
        qs = RegistroAsistenciaModel.objects.filter(empleado_id=empleado_id, timestamp__date=fecha).order_by("timestamp")
        return [self._to_entity(m) for m in qs]

    def get_ultimo_marcaje_del_dia(self, empleado_id: int, fecha: date) -> Optional[RegistroAsistencia]:
        model = (
            RegistroAsistenciaModel.objects
            .filter(empleado_id=empleado_id, timestamp__date=fecha)
            .order_by("-timestamp")
            .first()
        )
        return self._to_entity(model) if model else None

    def existe_marcaje_tipo_en_fecha(self, empleado_id: int, tipo: str, fecha: date) -> bool:
        return RegistroAsistenciaModel.objects.filter(
            empleado_id=empleado_id, tipo=tipo, timestamp__date=fecha
        ).exists()

    def get_by_empresa(
        self,
        empresa_id: int,
        fecha: Optional[date] = None,
        sede_id: Optional[int] = None,
        area: Optional[str] = None,
        solo_extras: bool = False,
        page: int = 1,
        page_size: int = 20,
    ) -> List[RegistroAsistencia]:
        qs = RegistroAsistenciaModel.objects.filter(empresa_id=empresa_id)
        if fecha:
            qs = qs.filter(timestamp__date=fecha)
        if sede_id:
            qs = qs.filter(sede_id=sede_id)
        if solo_extras:
            qs = qs.filter(minutos_extra__gt=0)
        offset = (page - 1) * page_size
        return [self._to_entity(m) for m in qs.order_by("-timestamp")[offset: offset + page_size]]

    def save(self, registro: RegistroAsistencia) -> RegistroAsistencia:
        if registro.id:
            model = RegistroAsistenciaModel.objects.get(pk=registro.id)
        else:
            model = RegistroAsistenciaModel()

        model.empresa_id = registro.empresa_id
        model.empleado_id = registro.empleado_id
        model.sede_id = registro.sede_id
        model.tipo = registro.tipo
        model.origen = registro.origen
        model.latitud = registro.coordenadas.latitud if registro.coordenadas else None
        model.longitud = registro.coordenadas.longitud if registro.coordenadas else None
        model.estado_auditoria = registro.estado_auditoria
        model.resultado = registro.resultado
        model.minutos_tardanza = registro.minutos_tardanza
        model.minutos_extra = registro.minutos_extra
        model.minutos_temprano = registro.minutos_temprano
        model.horas_trabajadas = registro.horas_trabajadas
        model.nivel_confianza = registro.nivel_confianza
        model.estado_extras = registro.estado_extras
        model.minutos_extra_aprobados = registro.minutos_extra_aprobados
        model.enviado_a_nomina = registro.enviado_a_nomina
        model.extras_evaluado_por_id = registro.extras_evaluado_por_id
        model.extras_fecha_evaluacion = registro.extras_fecha_evaluacion
        model.extras_comentario = registro.extras_comentario
        model.observaciones = registro.observaciones
        model.timestamp = registro.timestamp
        model.save()

        registro.id = model.pk
        return registro

    def count_by_empresa(
        self,
        empresa_id: int,
        fecha_desde: Optional[date] = None,
        fecha_hasta: Optional[date] = None,
    ) -> int:
        qs = RegistroAsistenciaModel.objects.filter(empresa_id=empresa_id)
        if fecha_desde:
            qs = qs.filter(timestamp__date__gte=fecha_desde)
        if fecha_hasta:
            qs = qs.filter(timestamp__date__lte=fecha_hasta)
        return qs.count()

    def _to_entity(self, model: RegistroAsistenciaModel) -> RegistroAsistencia:
        coordenadas = None
        if model.latitud is not None and model.longitud is not None:
            coordenadas = Coordenadas(float(model.latitud), float(model.longitud))
        return RegistroAsistencia(
            id=model.pk,
            empresa_id=model.empresa_id,
            empleado_id=model.empleado_id,
            sede_id=model.sede_id,
            tipo=model.tipo,
            origen=model.origen,
            coordenadas=coordenadas,
            estado_auditoria=model.estado_auditoria,
            resultado=model.resultado,
            minutos_tardanza=model.minutos_tardanza,
            minutos_extra=model.minutos_extra,
            minutos_temprano=model.minutos_temprano,
            horas_trabajadas=float(model.horas_trabajadas),
            nivel_confianza=model.nivel_confianza,
            estado_extras=model.estado_extras,
            minutos_extra_aprobados=model.minutos_extra_aprobados,
            enviado_a_nomina=model.enviado_a_nomina,
            extras_evaluado_por_id=model.extras_evaluado_por_id,
            extras_fecha_evaluacion=model.extras_fecha_evaluacion,
            extras_comentario=model.extras_comentario,
            observaciones=model.observaciones,
            timestamp=model.timestamp,
            fecha_creacion=model.fecha_creacion,
        )
