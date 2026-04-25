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
            if s.empleado_id not in empleados_cache:
                emp = self._empleado_repository.get_by_id(s.empleado_id)
                empleados_cache[s.empleado_id] = emp.nombre_completo() if emp else ""

            resultado.append(SolicitudOutputDTO(
                id=s.id,
                empresa_id=s.empresa_id,
                empleado_id=s.empleado_id,
                empleado_nombre=empleados_cache[s.empleado_id],
                tipo_permiso_id=s.tipo_permiso_id,
                tipo_permiso_nombre=s.tipo_permiso_nombre,
                fecha_inicio=s.fecha_inicio,
                fecha_fin=s.fecha_fin,
                dias_solicitados=s.dias_solicitados(),
                motivo=s.motivo,
                estado=s.estado,
                adjunto_url=s.adjunto_url,
                comentario_evaluador=s.comentario_evaluador,
                evaluado_por_id=s.evaluado_por_id,
                fecha_evaluacion=s.fecha_evaluacion,
                fecha_creacion=s.fecha_creacion,
            ))

        return resultado