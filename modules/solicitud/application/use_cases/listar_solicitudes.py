from typing import List
from shared.application.base_use_case import BaseUseCase
from modules.solicitud.domain.repositories.solicitud_repository import SolicitudRepository
from modules.empleado.domain.repositories.empleado_repository import EmpleadoRepository
from modules.solicitud.application.dtos.solicitud_dto import ListarSolicitudesInputDTO, SolicitudOutputDTO


class ListarSolicitudesUseCase(BaseUseCase[ListarSolicitudesInputDTO, List[SolicitudOutputDTO]]):
    def __init__(
        self,
        solicitud_repository: SolicitudRepository,
        empleado_repository: EmpleadoRepository,
    ):
        self._solicitud_repository = solicitud_repository
        self._empleado_repository = empleado_repository

    def execute(self, input_dto: ListarSolicitudesInputDTO) -> List[SolicitudOutputDTO]:
        solicitudes = self._solicitud_repository.get_by_empresa(
            empresa_id=input_dto.empresa_id,
            estado=input_dto.estado,
            empleado_id=input_dto.empleado_id,
            tipo_permiso_id=input_dto.tipo_permiso_id,
            fecha_desde=input_dto.fecha_desde,
            fecha_hasta=input_dto.fecha_hasta,
            page=input_dto.page,
            page_size=input_dto.page_size,
        )

        empleados_cache = {}
        resultado = []

        for s in solicitudes:
            try:
                # 1. Resolución segura del nombre del empleado
                if s.empleado_id not in empleados_cache:
                    emp = self._empleado_repository.get_by_id(s.empleado_id)
                    if emp:
                        # Verificamos si es un método () o una @property
                        if callable(getattr(emp, 'nombre_completo', None)):
                            empleados_cache[s.empleado_id] = emp.nombre_completo()
                        else:
                            empleados_cache[s.empleado_id] = getattr(emp, 'nombre_completo', f"Empleado {s.empleado_id}")
                    else:
                        empleados_cache[s.empleado_id] = "Empleado Desconocido"

                # 2. Resolución segura de los días solicitados
                if callable(getattr(s, 'dias_solicitados', None)):
                    dias = s.dias_solicitados()
                else:
                    dias = getattr(s, 'dias_solicitados', 0)
                    
                # Si no existe ni como método ni como propiedad, lo calculamos al vuelo
                if dias == 0 and hasattr(s, 'fecha_fin') and hasattr(s, 'fecha_inicio'):
                    delta = s.fecha_fin - s.fecha_inicio
                    dias = delta.days + 1

                # 3. Resolución segura del tipo de permiso (por si falta en la entidad)
                tipo_permiso = getattr(s, 'tipo_permiso_nombre', 'Permiso Estándar')

                # Construcción del DTO
                resultado.append(SolicitudOutputDTO(
                    id=s.id,
                    empresa_id=s.empresa_id,
                    empleado_id=s.empleado_id,
                    empleado_nombre=empleados_cache[s.empleado_id],
                    tipo_permiso_id=s.tipo_permiso_id,
                    tipo_permiso_nombre=tipo_permiso,
                    fecha_inicio=s.fecha_inicio,
                    fecha_fin=s.fecha_fin,
                    dias_solicitados=dias,
                    motivo=s.motivo,
                    estado=s.estado,
                    adjunto_url=s.adjunto_url,
                    comentario_evaluador=s.comentario_evaluador,
                    evaluado_por_id=s.evaluado_por_id,
                    fecha_evaluacion=s.fecha_evaluacion,
                    fecha_creacion=s.fecha_creacion,
                ))
            except Exception as e:
                import traceback
                print(f"❌ ERROR AL MAPEAR SOLICITUD ID {getattr(s, 'id', 'Desconocido')}: {str(e)}")
                traceback.print_exc()
                # Opcional: puedes hacer 'raise e' si quieres que el 500 siga apareciendo,
                # o dejar que continúe con el siguiente registro ignorando el que falló.
                raise e

        return resultado