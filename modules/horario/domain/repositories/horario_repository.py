from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import date
from modules.horario.domain.entities.horario import Horario, Turno, AsignacionHorario


class HorarioRepository(ABC):
    @abstractmethod
    def save_horario(self, horario: Horario) -> Horario:
        pass

    @abstractmethod
    def get_horario_by_id(self, id: int) -> Optional[Horario]:
        pass

    @abstractmethod
    def get_horarios_by_empresa(self, empresa_id: int, include_inactive: bool = False) -> List[Horario]:
        pass

    @abstractmethod
    def delete_horario(self, id: int) -> bool:
        pass


class TurnoRepository(ABC):
    @abstractmethod
    def save_turno(self, turno: Turno) -> Turno:
        pass

    @abstractmethod
    def get_turnos_by_horario(self, horario_id: int) -> List[Turno]:
        pass

    @abstractmethod
    def delete_turnos_by_horario(self, horario_id: int) -> None:
        pass


class AsignacionHorarioRepository(ABC):
    @abstractmethod
    def save_asignacion(self, asignacion: AsignacionHorario) -> AsignacionHorario:
        pass

    @abstractmethod
    def get_asignaciones_by_empleado(self, empleado_id: int) -> List[AsignacionHorario]:
        pass

    @abstractmethod
    def get_asignacion_activa(self, empleado_id: int, target_date: date) -> Optional[AsignacionHorario]:
        pass

    @abstractmethod
    def count_empleados_por_horario(self, horario_id: int, active_on: Optional[date] = None) -> int:
        pass
