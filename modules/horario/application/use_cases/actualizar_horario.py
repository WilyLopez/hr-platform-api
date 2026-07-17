from shared.application.base_use_case import BaseUseCase
from shared.domain.exceptions import EntityNotFoundException, InvalidValueException
from modules.horario.domain.entities.horario import Horario, Turno
from modules.horario.domain.repositories.horario_repository import HorarioRepository, TurnoRepository, AsignacionHorarioRepository
from modules.horario.application.dtos.horario_dto import ActualizarHorarioInputDTO, HorarioOutputDTO, TurnoOutputDTO

class ActualizarHorarioUseCase(BaseUseCase[ActualizarHorarioInputDTO, HorarioOutputDTO]):
    def __init__(
        self, 
        horario_repository: HorarioRepository, 
        turno_repository: TurnoRepository,
        asignacion_repository: AsignacionHorarioRepository
    ):
        self._horario_repository = horario_repository
        self._turno_repository = turno_repository
        self._asignacion_repository = asignacion_repository

    def execute(self, input_dto: ActualizarHorarioInputDTO) -> HorarioOutputDTO:
        horario = self._horario_repository.get_horario_by_id(input_dto.horario_id)
        if not horario or horario.empresa_id != input_dto.empresa_id:
            raise EntityNotFoundException("Horario", str(input_dto.horario_id))

        if not input_dto.turnos:
            raise InvalidValueException("Horario", "El horario debe tener al menos un turno.")

        horario.nombre = input_dto.nombre
        horario.descripcion = input_dto.descripcion
        horario.es_activo = input_dto.es_activo
        horario.tolerancia_ingreso_min = input_dto.tolerancia_ingreso_min
        horario.tolerancia_salida_min = input_dto.tolerancia_salida_min
        horario.horas_extras_permitidas = input_dto.horas_extras_permitidas
        horario.max_horas_extras_dia = input_dto.max_horas_extras_dia
        
        horario = self._horario_repository.save_horario(horario)

        # Para simplificar la actualización de turnos:
        # Se eliminan los antiguos y se crean los nuevos
        self._turno_repository.delete_turnos_by_horario(horario.id)
        
        turnos_output = []
        for t_dto in input_dto.turnos:
            turno = Turno(
                id=None,
                horario_id=horario.id,
                dia_semana=t_dto.dia_semana,
                hora_inicio=t_dto.hora_inicio,
                hora_fin=t_dto.hora_fin,
                minutos_refrigerio=t_dto.minutos_refrigerio,
                es_laborable=t_dto.es_laborable,
            )
            turno = self._turno_repository.save_turno(turno)
            turnos_output.append(TurnoOutputDTO(
                id=turno.id,
                horario_id=turno.horario_id,
                dia_semana=turno.dia_semana,
                hora_inicio=turno.hora_inicio,
                hora_fin=turno.hora_fin,
                minutos_refrigerio=turno.minutos_refrigerio,
                es_laborable=turno.es_laborable,
            ))

        empleados_asignados = self._asignacion_repository.count_empleados_por_horario(horario.id)

        return HorarioOutputDTO(
            id=horario.id,
            nombre=horario.nombre,
            descripcion=horario.descripcion,
            es_activo=horario.es_activo,
            tolerancia_ingreso_min=horario.tolerancia_ingreso_min,
            tolerancia_salida_min=horario.tolerancia_salida_min,
            horas_extras_permitidas=horario.horas_extras_permitidas,
            max_horas_extras_dia=horario.max_horas_extras_dia,
            turnos=turnos_output,
            empleados_asignados=empleados_asignados
        )
