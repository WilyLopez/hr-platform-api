from datetime import date, datetime
from django.utils import timezone
from shared.application.base_use_case import BaseUseCase
from shared.constants import TiposMarcaje
from modules.asistencia.domain.repositories.asistencia_repository import AsistenciaRepository
from modules.horario.domain.repositories.horario_repository import AsignacionHorarioRepository, TurnoRepository, HorarioRepository
from modules.empleado.domain.repositories.empleado_repository import EmpleadoRepository
from modules.asistencia.application.dtos.asistencia_dto import EstadoAsistenciaHoyDTO


from modules.asistencia.domain.services.disponibilidad_laboral_service import DisponibilidadLaboralService

class ObtenerEstadoAsistenciaHoyUseCase(BaseUseCase[int, EstadoAsistenciaHoyDTO]):
    def __init__(
        self,
        asistencia_repository: AsistenciaRepository,
        asignacion_repository: AsignacionHorarioRepository,
        horario_repository: HorarioRepository,
        turno_repository: TurnoRepository,
        empleado_repository: EmpleadoRepository,
        disponibilidad_service: DisponibilidadLaboralService,
    ):
        self._asistencia_repository = asistencia_repository
        self._asignacion_repository = asignacion_repository
        self._horario_repository = horario_repository
        self._turno_repository = turno_repository
        self._empleado_repository = empleado_repository
        self._disponibilidad_service = disponibilidad_service

    def execute(self, usuario_id: int) -> EstadoAsistenciaHoyDTO:
        empleado = self._empleado_repository.get_by_usuario_id(usuario_id)
        if not empleado:
            raise ValueError("Empleado no encontrado.")

        hoy = timezone.localdate()
        now = timezone.localtime()

        asignacion = self._asignacion_repository.get_asignacion_activa(empleado.id, hoy)
        horario_hoy_str = "No asignado"
        turno_hoy = None

        if asignacion:
            horario = self._horario_repository.get_horario_by_id(asignacion.horario_id)
            turnos = self._turno_repository.get_turnos_by_horario(horario.id)
            turno_hoy = next((t for t in turnos if t.dia_semana == hoy.weekday()), None)

            if turno_hoy and turno_hoy.es_laborable:
                horario_hoy_str = f"{turno_hoy.hora_inicio.strftime('%H:%M')} - {turno_hoy.hora_fin.strftime('%H:%M')}"
            else:
                horario_hoy_str = "Día Libre"

        marcajes = self._asistencia_repository.get_marcajes_del_dia(empleado.id, hoy)
        
        # Evaluar disponibilidad (Permisos / Vacaciones / Descanso)
        _, disp_estado, disp_justificacion = self._disponibilidad_service.evaluar_disponibilidad(empleado.id, hoy, now.time())
        
        estado_actual = disp_estado
        if disp_estado == "SIN_MARCAR" and disp_justificacion:
            horario_hoy_str += f" ({disp_justificacion})"
        elif disp_estado in ["DE_PERMISO", "VACACIONES"] and disp_justificacion:
            horario_hoy_str = disp_justificacion
        ultimo_marcaje_str = None
        tiempo_trabajado_min = 0

        if marcajes:
            ultimo_m = marcajes[-1]
            tipo_display = self._get_tipo_display(ultimo_m.tipo)
            local_time = timezone.localtime(ultimo_m.timestamp)
            ultimo_marcaje_str = f"{tipo_display} {local_time.strftime('%H:%M')}"

            if ultimo_m.tipo == TiposMarcaje.ENTRADA:
                estado_actual = "TRABAJANDO"
            elif ultimo_m.tipo == TiposMarcaje.INICIO_REFRIGERIO:
                estado_actual = "EN_REFRIGERIO"
            elif ultimo_m.tipo == TiposMarcaje.FIN_REFRIGERIO:
                estado_actual = "TRABAJANDO"
            elif ultimo_m.tipo == TiposMarcaje.SALIDA:
                estado_actual = "FINALIZADO"

            tiempo_trabajado_min = self._calcular_tiempo_trabajado(marcajes, now)

        horas = tiempo_trabajado_min // 60
        minutos = tiempo_trabajado_min % 60
        tiempo_trabajado_str = f"{horas}h {minutos}m"

        return EstadoAsistenciaHoyDTO(
            estado_actual=estado_actual,
            horario_hoy=horario_hoy_str,
            ultimo_marcaje=ultimo_marcaje_str,
            tiempo_trabajado_str=tiempo_trabajado_str,
            tiempo_trabajado_minutos=tiempo_trabajado_min
        )

    def _get_tipo_display(self, tipo: str) -> str:
        if tipo == TiposMarcaje.ENTRADA:
            return "Entrada"
        if tipo == TiposMarcaje.INICIO_REFRIGERIO:
            return "Inicio Ref."
        if tipo == TiposMarcaje.FIN_REFRIGERIO:
            return "Fin Ref."
        if tipo == TiposMarcaje.SALIDA:
            return "Salida"
        return tipo

    def _calcular_tiempo_trabajado(self, marcajes, now: datetime) -> int:
        total_minutos = 0
        entrada = None
        
        for m in marcajes:
            if m.tipo == TiposMarcaje.ENTRADA or m.tipo == TiposMarcaje.FIN_REFRIGERIO:
                entrada = m.timestamp
            elif m.tipo == TiposMarcaje.SALIDA or m.tipo == TiposMarcaje.INICIO_REFRIGERIO:
                if entrada:
                    total_minutos += int((m.timestamp - entrada).total_seconds() / 60)
                    entrada = None
                    
        # Si sigue trabajando, sumar hasta 'now'
        if entrada:
            total_minutos += int((now - entrada).total_seconds() / 60)
            
        return max(0, total_minutos)
