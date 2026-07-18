from typing import List, Optional
from datetime import date
from django.db import transaction
from django.db.models import Count, Q
from modules.horario.domain.entities.horario import Horario, Turno, AsignacionHorario
from modules.horario.domain.repositories.horario_repository import (
    HorarioRepository,
    TurnoRepository,
    AsignacionHorarioRepository
)
from modules.horario.infrastructure.models.horario_model import (
    HorarioModel,
    TurnoModel,
    AsignacionHorarioModel
)


class DjangoHorarioRepository(HorarioRepository):
    def save_horario(self, horario: Horario) -> Horario:
        with transaction.atomic():
            if horario.id:
                model = HorarioModel.objects.get(pk=horario.id)
            else:
                model = HorarioModel()

            model.empresa_id = horario.empresa_id
            model.nombre = horario.nombre
            model.descripcion = horario.descripcion
            model.es_activo = horario.es_activo
            model.tolerancia_ingreso_min = horario.tolerancia_ingreso_min
            model.tolerancia_salida_min = horario.tolerancia_salida_min
            model.horas_extras_permitidas = horario.horas_extras_permitidas
            model.max_horas_extras_dia = horario.max_horas_extras_dia
            model.fecha_actualizacion = horario.fecha_actualizacion
            model.save()
            
            horario.id = model.pk
            horario.fecha_creacion = model.fecha_creacion
            return horario

    def get_horario_by_id(self, id: int) -> Optional[Horario]:
        try:
            model = HorarioModel.objects.get(pk=id)
            return self._to_entity(model)
        except HorarioModel.DoesNotExist:
            return None

    def get_horarios_by_empresa(self, empresa_id: int, include_inactive: bool = False) -> List[Horario]:
        qs = HorarioModel.objects.filter(empresa_id=empresa_id)
        if not include_inactive:
            qs = qs.filter(es_activo=True)
        return [self._to_entity(m) for m in qs]

    def delete_horario(self, id: int) -> bool:
        try:
            model = HorarioModel.objects.get(pk=id)
            model.delete()
            return True
        except HorarioModel.DoesNotExist:
            return False

    def _to_entity(self, model: HorarioModel) -> Horario:
        horario = Horario(
            id=model.pk,
            empresa_id=model.empresa_id,
            nombre=model.nombre,
            descripcion=model.descripcion,
            es_activo=model.es_activo,
            tolerancia_ingreso_min=model.tolerancia_ingreso_min,
            tolerancia_salida_min=model.tolerancia_salida_min,
            horas_extras_permitidas=model.horas_extras_permitidas,
            max_horas_extras_dia=model.max_horas_extras_dia,
            fecha_creacion=model.fecha_creacion,
            fecha_actualizacion=model.fecha_actualizacion
        )
        # We don't eagerly load turnos here to avoid N+1 if not needed.
        # But for full aggregate we could.
        return horario


class DjangoTurnoRepository(TurnoRepository):
    def save_turno(self, turno: Turno) -> Turno:
        if turno.id:
            model = TurnoModel.objects.get(pk=turno.id)
        else:
            model = TurnoModel()

        model.horario_id = turno.horario_id
        model.dia_semana = turno.dia_semana
        model.hora_inicio = turno.hora_inicio
        model.hora_fin = turno.hora_fin
        model.minutos_refrigerio = turno.minutos_refrigerio
        model.es_laborable = turno.es_laborable
        model.save()
        
        turno.id = model.pk
        return turno

    def get_turnos_by_horario(self, horario_id: int) -> List[Turno]:
        models = TurnoModel.objects.filter(horario_id=horario_id).order_by('dia_semana')
        return [self._to_entity(m) for m in models]

    def delete_turnos_by_horario(self, horario_id: int) -> None:
        TurnoModel.objects.filter(horario_id=horario_id).delete()

    def _to_entity(self, model: TurnoModel) -> Turno:
        return Turno(
            id=model.pk,
            horario_id=model.horario_id,
            dia_semana=model.dia_semana,
            hora_inicio=model.hora_inicio,
            hora_fin=model.hora_fin,
            minutos_refrigerio=model.minutos_refrigerio,
            es_laborable=model.es_laborable
        )


class DjangoAsignacionHorarioRepository(AsignacionHorarioRepository):
    def save_asignacion(self, asignacion: AsignacionHorario) -> AsignacionHorario:
        if asignacion.id:
            model = AsignacionHorarioModel.objects.get(pk=asignacion.id)
        else:
            model = AsignacionHorarioModel()

        model.empleado_id = asignacion.empleado_id
        model.horario_id = asignacion.horario_id
        model.fecha_desde = asignacion.fecha_desde
        model.fecha_hasta = asignacion.fecha_hasta
        model.creado_por_id = asignacion.creado_por_id
        model.save()

        asignacion.id = model.pk
        asignacion.fecha_creacion = model.fecha_creacion
        return asignacion

    def get_asignaciones_by_empleado(self, empleado_id: int) -> List[AsignacionHorario]:
        models = AsignacionHorarioModel.objects.filter(empleado_id=empleado_id).order_by('-fecha_desde')
        return [self._to_entity(m) for m in models]

    def get_asignacion_activa(self, empleado_id: int, target_date: date) -> Optional[AsignacionHorario]:
        # Activa si target_date >= fecha_desde AND (fecha_hasta is null OR target_date <= fecha_hasta)
        model = AsignacionHorarioModel.objects.filter(
            empleado_id=empleado_id,
            fecha_desde__lte=target_date
        ).filter(
            Q(fecha_hasta__isnull=True) | Q(fecha_hasta__gte=target_date)
        ).order_by('-fecha_desde').first()
        
        if model:
            return self._to_entity(model)
        return None

    def count_empleados_por_horario(self, horario_id: int, active_on: Optional[date] = None) -> int:
        qs = AsignacionHorarioModel.objects.filter(horario_id=horario_id)
        if active_on:
            qs = qs.filter(fecha_desde__lte=active_on).filter(
                Q(fecha_hasta__isnull=True) | Q(fecha_hasta__gte=active_on)
            )
        return qs.values('empleado_id').distinct().count()

    def _to_entity(self, model: AsignacionHorarioModel) -> AsignacionHorario:
        return AsignacionHorario(
            id=model.pk,
            empleado_id=model.empleado_id,
            horario_id=model.horario_id,
            fecha_desde=model.fecha_desde,
            fecha_hasta=model.fecha_hasta,
            fecha_creacion=model.fecha_creacion,
            creado_por_id=model.creado_por_id
        )
