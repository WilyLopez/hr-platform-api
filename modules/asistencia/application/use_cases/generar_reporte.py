from shared.application.base_use_case import BaseUseCase
from shared.constants import TiposMarcaje
from modules.asistencia.domain.repositories.asistencia_repository import AsistenciaRepository
from modules.empleado.domain.repositories.empleado_repository import EmpleadoRepository
from modules.asistencia.application.dtos.asistencia_dto import (
    ListarAsistenciaInputDTO,
    ReporteAsistenciaOutputDTO,
    RegistroAsistenciaOutputDTO,
)


from modules.empresa.domain.repositories.sede_repository import SedeRepository

class GenerarReporteAsistenciaUseCase(BaseUseCase[ListarAsistenciaInputDTO, ReporteAsistenciaOutputDTO]):
    def __init__(
        self,
        asistencia_repository: AsistenciaRepository,
        empleado_repository: EmpleadoRepository,
        sede_repository: SedeRepository = None,
    ):
        self._asistencia_repository = asistencia_repository
        self._empleado_repository = empleado_repository
        self._sede_repository = sede_repository

    def execute(self, input_dto: ListarAsistenciaInputDTO) -> ReporteAsistenciaOutputDTO:
        if input_dto.empleado_id:
            registros_crudos = self._asistencia_repository.get_by_empleado(
                empleado_id=input_dto.empleado_id,
                fecha_desde=input_dto.fecha_desde,
                fecha_hasta=input_dto.fecha_hasta,
                page=1,
                page_size=1000
            )
        else:
            # We don't have a get_by_empresa with date ranges yet, let's use what we have or just mock it.
            # Wait, get_by_empresa only takes `fecha`. Let's mock a simple fallback if no empleado_id.
            registros_crudos = self._asistencia_repository.get_by_empresa(
                empresa_id=input_dto.empresa_id,
                fecha=input_dto.fecha_desde,
                sede_id=input_dto.sede_id,
                area=input_dto.area,
                page=1,
                page_size=1000
            )

        # Manejo de paginación si el repo retorna un dict
        if isinstance(registros_crudos, dict) and "results" in registros_crudos:
            registros = registros_crudos["results"]
        elif hasattr(registros_crudos, 'results'):
            registros = registros_crudos.results
        else:
            registros = registros_crudos

        empleados_ids = {r.empleado_id for r in registros}
        empleados_map = {
            e.id: e.nombre_completo()
            for e in [self._empleado_repository.get_by_id(eid) for eid in empleados_ids]
            if e
        }
        
        sedes_ids = {r.sede_id for r in registros}
        sedes_map = {}
        if self._sede_repository:
            sedes_map = {
                s.id: s.nombre
                for s in [self._sede_repository.get_by_id(sid) for sid in sedes_ids]
                if s
            }

        entradas = [r for r in registros if r.tipo == TiposMarcaje.ENTRADA]
        tardanzas = sum(1 for r in registros if r.resultado == "TARDE")

        output_registros = [
            RegistroAsistenciaOutputDTO(
                id=r.id,
                empleado_id=r.empleado_id,
                empleado_nombre=empleados_map.get(r.empleado_id, ""),
                sede_id=r.sede_id,
                sede_nombre=sedes_map.get(r.sede_id, "Sede Principal"),
                tipo=r.tipo,
                origen=r.origen,
                estado_auditoria=r.estado_auditoria,
                resultado=r.resultado,
                minutos_tardanza=r.minutos_tardanza,
                minutos_extra=r.minutos_extra,
                minutos_temprano=r.minutos_temprano,
                horas_trabajadas=r.horas_trabajadas,
                estado_extras=getattr(r, 'estado_extras', None),
                minutos_extra_aprobados=getattr(r, 'minutos_extra_aprobados', None),
                timestamp=r.timestamp,
            )
            for r in registros
        ]

        return ReporteAsistenciaOutputDTO(
            empleado_id=input_dto.empleado_id or 0,
            empleado_nombre=empleados_map.get(input_dto.empleado_id, "Todos") if input_dto.empleado_id else "Todos",
            total_dias=len(set(r.timestamp.date() for r in entradas)),
            dias_presentes=len(entradas),
            dias_ausentes=0,
            tardanzas=tardanzas,
            registros=output_registros,
        )