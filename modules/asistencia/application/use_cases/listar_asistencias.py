from typing import List
from shared.application.base_use_case import BaseUseCase
from modules.asistencia.domain.repositories.asistencia_repository import AsistenciaRepository
from modules.empleado.domain.repositories.empleado_repository import EmpleadoRepository
from modules.asistencia.application.dtos.asistencia_dto import ListarAsistenciaInputDTO, RegistroAsistenciaOutputDTO

class ListarAsistenciasUseCase(BaseUseCase[ListarAsistenciaInputDTO, List[RegistroAsistenciaOutputDTO]]):
    def __init__(
        self,
        asistencia_repository: AsistenciaRepository,
        empleado_repository: EmpleadoRepository,
    ):
        self._asistencia_repository = asistencia_repository
        self._empleado_repository = empleado_repository

    def execute(self, input_dto: ListarAsistenciaInputDTO) -> List[RegistroAsistenciaOutputDTO]:
        # 1. Enrutador inteligente: decidimos qué método del repositorio usar
        if input_dto.empleado_id:
            # Si el frontend busca a un empleado en específico
            asistencias_crudas = self._asistencia_repository.get_by_empleado(
                empleado_id=input_dto.empleado_id,
                fecha_desde=input_dto.fecha_desde,
                fecha_hasta=input_dto.fecha_hasta,
                page=input_dto.page,
                page_size=input_dto.page_size
            )
        else:
            # Si el frontend busca el listado general del día (Dashboard/Bandeja)
            asistencias_crudas = self._asistencia_repository.get_by_empresa(
                empresa_id=input_dto.empresa_id,
                fecha=input_dto.fecha_desde, # get_by_empresa usa 'fecha' (día único)
                sede_id=input_dto.sede_id,
                area=input_dto.area,
                page=input_dto.page,
                page_size=input_dto.page_size
            )

        empleados_cache = {}
        resultado = []

        # 2. Protección por si el repositorio devuelve algo distinto a una lista
        lista_asistencias = []
        if isinstance(asistencias_crudas, dict) and "results" in asistencias_crudas:
            lista_asistencias = asistencias_crudas["results"]
        elif hasattr(asistencias_crudas, 'results'):
            lista_asistencias = asistencias_crudas.results
        else:
            lista_asistencias = asistencias_crudas

        # 3. Mapeo seguro a DTOs
        for a in lista_asistencias:
            try:
                # Resolución del nombre del empleado
                if a.empleado_id not in empleados_cache:
                    emp = self._empleado_repository.get_by_id(a.empleado_id)
                    if emp:
                        if callable(getattr(emp, 'nombre_completo', None)):
                            empleados_cache[a.empleado_id] = emp.nombre_completo()
                        else:
                            empleados_cache[a.empleado_id] = getattr(emp, 'nombre_completo', f"Empleado {a.empleado_id}")
                    else:
                        empleados_cache[a.empleado_id] = "Empleado Desconocido"

                # Resolución de la sede
                sede_nombre = getattr(a, 'sede_nombre', f"Sede {getattr(a, 'sede_id', 'Desconocida')}")

                resultado.append(RegistroAsistenciaOutputDTO(
                    id=a.id,
                    empleado_id=a.empleado_id,
                    empleado_nombre=empleados_cache[a.empleado_id],
                    sede_id=a.sede_id,
                    sede_nombre=sede_nombre,
                    tipo=a.tipo,
                    metodo=a.metodo,
                    es_tardanza=a.es_tardanza,
                    es_manual=a.es_manual,
                    timestamp=a.timestamp
                ))
            except Exception as e:
                import traceback
                print(f"❌ ERROR AL MAPEAR ASISTENCIA ID {getattr(a, 'id', 'Desconocido')}: {str(e)}")
                traceback.print_exc()

        return resultado