from datetime import datetime
from django.utils import timezone
from shared.application.base_use_case import BaseUseCase
from shared.constants import EstadosHorasExtras
from modules.asistencia.domain.repositories.asistencia_repository import AsistenciaRepository
from dataclasses import dataclass
from typing import Optional

@dataclass
class AprobarHorasExtrasInputDTO:
    registro_id: int
    evaluador_id: int
    minutos_aprobados: int
    comentario: Optional[str] = None
    aprobar: bool = True  # True para aprobar, False para rechazar


class AprobarHorasExtrasUseCase(BaseUseCase[AprobarHorasExtrasInputDTO, bool]):
    def __init__(self, asistencia_repository: AsistenciaRepository):
        self._asistencia_repository = asistencia_repository

    def execute(self, input_dto: AprobarHorasExtrasInputDTO) -> bool:
        registro = self._asistencia_repository.get_by_id(input_dto.registro_id)
        
        if not registro:
            raise ValueError("Registro de asistencia no encontrado.")
            
        if registro.minutos_extra <= 0:
            raise ValueError("El registro no tiene horas extras que aprobar.")
            
        if registro.estado_extras in [EstadosHorasExtras.APROBADA, EstadosHorasExtras.RECHAZADA]:
            raise ValueError("Las horas extras de este registro ya fueron evaluadas.")

        if input_dto.aprobar:
            if input_dto.minutos_aprobados < 0 or input_dto.minutos_aprobados > registro.minutos_extra:
                raise ValueError(f"Minutos aprobados inválidos. Máximo: {registro.minutos_extra} min.")
            
            registro.estado_extras = EstadosHorasExtras.APROBADA
            registro.minutos_extra_aprobados = input_dto.minutos_aprobados
        else:
            registro.estado_extras = EstadosHorasExtras.RECHAZADA
            registro.minutos_extra_aprobados = 0

        registro.extras_evaluado_por_id = input_dto.evaluador_id
        registro.extras_fecha_evaluacion = timezone.localtime()
        registro.extras_comentario = input_dto.comentario
        
        self._asistencia_repository.save(registro)
        return True
