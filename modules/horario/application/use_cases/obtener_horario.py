from shared.application.base_use_case import BaseUseCase
from shared.domain.exceptions import EntityNotFoundException
from modules.horario.domain.repositories.horario_repository import HorarioRepository, TurnoRepository, AsignacionHorarioRepository
from modules.horario.application.dtos.horario_dto import HorarioOutputDTO, TurnoOutputDTO

class ObtenerHorarioUseCase(BaseUseCase[int, HorarioOutputDTO]):
    def __init__(
        self, 
        horario_repository: HorarioRepository, 
        turno_repository: TurnoRepository,
        asignacion_repository: AsignacionHorarioRepository
    ):
        self._horario_repository = horario_repository
        self._turno_repository = turno_repository
        self._asignacion_repository = asignacion_repository

    def execute(self, horario_id: int) -> HorarioOutputDTO:
        h = self._horario_repository.get_horario_by_id(horario_id)
        if not h:
            raise EntityNotFoundException("Horario", str(horario_id))
            
        turnos = self._turno_repository.get_turnos_by_horario(h.id)
        empleados_asignados = self._asignacion_repository.count_empleados_por_horario(h.id)
        
        turnos_output = [TurnoOutputDTO(
            id=t.id,
            horario_id=t.horario_id,
            dia_semana=t.dia_semana,
            hora_inicio=t.hora_inicio,
            hora_fin=t.hora_fin,
            minutos_refrigerio=t.minutos_refrigerio,
            es_laborable=t.es_laborable,
        ) for t in turnos]

        return HorarioOutputDTO(
            id=h.id,
            nombre=h.nombre,
            descripcion=h.descripcion,
            es_activo=h.es_activo,
            tolerancia_ingreso_min=h.tolerancia_ingreso_min,
            tolerancia_salida_min=h.tolerancia_salida_min,
            horas_extras_permitidas=h.horas_extras_permitidas,
            max_horas_extras_dia=h.max_horas_extras_dia,
            turnos=turnos_output,
            empleados_asignados=empleados_asignados
        )
