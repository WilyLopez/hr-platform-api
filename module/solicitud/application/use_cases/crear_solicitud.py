from datetime import datetime
from shared.application.base_use_case import BaseUseCase
from shared.constants import EstadosSolicitud, TiposEvento
from modules.solicitud.domain.entities.solicitud import Solicitud
from modules.solicitud.domain.repositories.solicitud_repository import SolicitudRepository
from modules.solicitud.domain.repositories.tipo_permiso_repository import TipoPermisoRepository
from modules.solicitud.domain.exceptions import TipoPermisoNoEncontradoException
from modules.empleado.domain.repositories.empleado_repository import EmpleadoRepository
from modules.empleado.domain.exceptions import EmpleadoNoEncontradoException
from modules.solicitud.application.dtos.solicitud_dto import CrearSolicitudInputDTO, SolicitudOutputDTO


class CrearSolicitudUseCase(BaseUseCase[CrearSolicitudInputDTO, SolicitudOutputDTO]):
    def __init__(
        self,
        solicitud_repository: SolicitudRepository,
        tipo_permiso_repository: TipoPermisoRepository,
        empleado_repository: EmpleadoRepository,
        auditoria_use_case,
        notificacion_use_case,
    ):
        self._solicitud_repository = solicitud_repository
        self._tipo_permiso_repository = tipo_permiso_repository
        self._empleado_repository = empleado_repository
        self._auditoria_use_case = auditoria_use_case
        self._notificacion_use_case = notificacion_use_case

    def execute(self, input_dto: CrearSolicitudInputDTO) -> SolicitudOutputDTO:
        empleado = self._empleado_repository.get_by_id(input_dto.empleado_id)
        if not empleado or empleado.empresa_id != input_dto.empresa_id:
            raise EmpleadoNoEncontradoException(str(input_dto.empleado_id))

        tipo = self._tipo_permiso_repository.get_by_id(input_dto.tipo_permiso_id)
        if not tipo or tipo.empresa_id != input_dto.empresa_id:
            raise TipoPermisoNoEncontradoException(str(input_dto.tipo_permiso_id))

        solicitud = Solicitud(
            id=None,
            empresa_id=input_dto.empresa_id,
            empleado_id=input_dto.empleado_id,
            tipo_permiso_id=input_dto.tipo_permiso_id,
            tipo_permiso_nombre=tipo.nombre,
            fecha_inicio=input_dto.fecha_inicio,
            fecha_fin=input_dto.fecha_fin,
            motivo=input_dto.motivo,
            estado=EstadosSolicitud.PENDIENTE,
            adjunto_url=input_dto.adjunto_url,
            comentario_evaluador=None,
            evaluado_por_id=None,
            fecha_evaluacion=None,
            fecha_creacion=datetime.now(),
            fecha_actualizacion=None,
        )

        solicitud = self._solicitud_repository.save(solicitud)

        self._notificacion_use_case.notificar_nueva_solicitud(
            empresa_id=input_dto.empresa_id,
            empleado_nombre=empleado.nombre_completo(),
            tipo_permiso=tipo.nombre,
            fecha_inicio=input_dto.fecha_inicio,
            fecha_fin=input_dto.fecha_fin,
        )
        self._auditoria_use_case.registrar(
            empresa_id=input_dto.empresa_id,
            usuario_id=empleado.usuario_id,
            tipo_evento=TiposEvento.CREACION_SOLICITUD,
            descripcion=f"Solicitud de {tipo.nombre} creada.",
            ip_address=None,
            detalles={"solicitud_id": solicitud.id},
        )

        return self._to_output(solicitud, empleado.nombre_completo())

    def _to_output(self, solicitud: Solicitud, empleado_nombre: str) -> SolicitudOutputDTO:
        return SolicitudOutputDTO(
            id=solicitud.id,
            empresa_id=solicitud.empresa_id,
            empleado_id=solicitud.empleado_id,
            empleado_nombre=empleado_nombre,
            tipo_permiso_id=solicitud.tipo_permiso_id,
            tipo_permiso_nombre=solicitud.tipo_permiso_nombre,
            fecha_inicio=solicitud.fecha_inicio,
            fecha_fin=solicitud.fecha_fin,
            dias_solicitados=solicitud.dias_solicitados(),
            motivo=solicitud.motivo,
            estado=solicitud.estado,
            adjunto_url=solicitud.adjunto_url,
            comentario_evaluador=solicitud.comentario_evaluador,
            evaluado_por_id=solicitud.evaluado_por_id,
            fecha_evaluacion=solicitud.fecha_evaluacion,
            fecha_creacion=solicitud.fecha_creacion,
        )