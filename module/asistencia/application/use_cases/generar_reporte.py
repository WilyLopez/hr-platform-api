from shared.application.base_use_case import BaseUseCase
from shared.constants import TiposMarcaje
from modules.asistencia.domain.repositories.asistencia_repository import AsistenciaRepository
from modules.empleado.domain.repositories.empleado_repository import EmpleadoRepository
from modules.asistencia.application.dtos.asistencia_dto import (
    ListarAsistenciaInputDTO,
    ReporteAsistenciaOutputDTO,
    RegistroAsistenciaOutputDTO,
)


class GenerarReporteAsistenciaUseCase(BaseUseCase[ListarAsistenciaInputDTO, ReporteAsistenciaOutputDTO]):
    def __init__(
        self,
        asistencia_repository: AsistenciaRepository,
        empleado_repository: EmpleadoRepository,
    ):
        self._asistencia_repository = asistencia_repository
        self._empleado_repository = empleado_repository

    def execute(self, input_dto: ListarAsistenciaInputDTO) -> ReporteAsistenciaOutputDTO:
        registros = self._asistencia_repository.get_by_empresa(
            empresa_id=input_dto.empresa_id,
            empleado_id=input_dto.empleado_id,
            sede_id=input_dto.sede_id,
            area=input_dto.area,
            fecha_desde=input_dto.fecha_desde,
            fecha_hasta=input_dto.fecha_hasta,
        )

        empleados_ids = {r.empleado_id for r in registros}
        empleados_map = {
            e.id: e.nombre_completo()
            for e in [self._empleado_repository.get_by_id(eid) for eid in empleados_ids]
            if e
        }

        entradas = [r for r in registros if r.tipo == TiposMarcaje.ENTRADA]
        tardanzas = sum(1 for r in entradas if r.es_tardanza)

        output_registros = [
            RegistroAsistenciaOutputDTO(
                id=r.id,
                empleado_id=r.empleado_id,
                empleado_nombre=empleados_map.get(r.empleado_id, ""),
                sede_id=r.sede_id,
                sede_nombre=None,
                tipo=r.tipo,
                metodo=r.metodo,
                es_tardanza=r.es_tardanza,
                es_manual=r.es_manual,
                timestamp=r.timestamp,
            )
            for r in registros
        ]

        return ReporteAsistenciaOutputDTO(
            empleado_id=input_dto.empleado_id or 0,
            empleado_nombre=empleados_map.get(input_dto.empleado_id, "Todos"),
            total_dias=len(set(r.timestamp.date() for r in entradas)),
            dias_presentes=len(entradas),
            dias_ausentes=0,
            tardanzas=tardanzas,
            registros=output_registros,
        )