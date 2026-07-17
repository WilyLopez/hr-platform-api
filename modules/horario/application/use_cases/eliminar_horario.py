from shared.application.base_use_case import BaseUseCase
from shared.domain.exceptions import EntityNotFoundException, BusinessRuleViolationException
from modules.horario.domain.repositories.horario_repository import HorarioRepository, AsignacionHorarioRepository

class HorarioEnUsoException(BusinessRuleViolationException):
    def __init__(self):
        super().__init__(
            message="No se puede eliminar el horario porque tiene empleados asignados en su historial. Por favor, desactívelo en su lugar.",
            code="horario_en_uso"
        )


class EliminarHorarioUseCase(BaseUseCase[int, bool]):
    def __init__(
        self,
        horario_repository: HorarioRepository,
        asignacion_repository: AsignacionHorarioRepository
    ):
        self._horario_repository = horario_repository
        self._asignacion_repository = asignacion_repository

    def execute(self, horario_id: int) -> bool:
        horario = self._horario_repository.get_horario_by_id(horario_id)
        if not horario:
            raise EntityNotFoundException("Horario", str(horario_id))
            
        # Comprobar si hay asignaciones
        empleados_asignados = self._asignacion_repository.count_empleados_por_horario(horario_id)
        if empleados_asignados > 0:
            raise HorarioEnUsoException()
            
        return self._horario_repository.delete_horario(horario_id)
