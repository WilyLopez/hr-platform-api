from shared.application.base_use_case import BaseUseCase
from modules.solicitud.domain.repositories.solicitud_repository import SolicitudRepository
from modules.empleado.domain.repositories.empleado_repository import EmpleadoRepository
from modules.solicitud.domain.exceptions import SolicitudNoEncontradaException
from modules.solicitud.application.dtos.solicitud_dto import SolicitudOutputDTO
from dataclasses import dataclass


@dataclass
class ObtenerSolicitudInputDTO:
    solicitud_id: int
    empresa_id: int


class ObtenerSolicitudUseCase(BaseUseCase[ObtenerSolicitudInputDTO, SolicitudOutputDTO]):
    def __init__(
        self,
        solicitud_repository: SolicitudRepository,
        empleado_repository: EmpleadoRepository,
    ):
        self._solicitud_repository = solicitud_repository
        self._empleado_repository = empleado_repository

    def execute(self, input_dto: ObtenerSolicitudInputDTO) -> SolicitudOutputDTO:
        solicitud = self._solicitud_repository.get_by_id(input_dto.solicitud_id)
        if not solicitud or solicitud.empresa_id != input_dto.empresa_id:
            raise SolicitudNoEncontradaException(str(input_dto.solicitud_id))

        empleado = self._empleado_repository.get_by_id(solicitud.empleado_id)
        
        return SolicitudOutputDTO(
            id=solicitud.id,
            empresa_id=solicitud.empresa_id,
            empleado_id=solicitud.empleado_id,
            empleado_nombre=empleado.nombre_completo() if empleado else "Desconocido",
            tipo_permiso_id=solicitud.tipo_permiso_id,
            tipo_permiso_nombre=solicitud.tipo_permiso_nombre,
            fecha_inicio=solicitud.fecha_inicio,
            fecha_fin=solicitud.fecha_fin,
            hora_inicio=solicitud.hora_inicio.strftime('%H:%M') if solicitud.hora_inicio else None,
            hora_fin=solicitud.hora_fin.strftime('%H:%M') if solicitud.hora_fin else None,
            dias_solicitados=solicitud.dias_solicitados(),
            motivo=solicitud.motivo,
            estado=solicitud.estado,
            adjunto_url=solicitud.adjunto_url,
            comentario_evaluador=solicitud.comentario_evaluador,
            evaluado_por_id=solicitud.evaluado_por_id,
            fecha_evaluacion=solicitud.fecha_evaluacion,
            fecha_creacion=solicitud.fecha_actualizacion, # Fallback if no creation date
        )
