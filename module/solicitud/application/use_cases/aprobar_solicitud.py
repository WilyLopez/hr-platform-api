from shared.application.base_use_case import BaseUseCase
from shared.constants import TiposEvento
from modules.solicitud.domain.repositories.solicitud_repository import SolicitudRepository
from modules.solicitud.domain.exceptions import SolicitudNoEncontradaException
from modules.empleado.domain.repositories.empleado_repository import EmpleadoRepository
from modules.solicitud.application.dtos.solicitud_dto import EvaluarSolicitudInputDTO, SolicitudOutputDTO


class AprobarSolicitudUseCase(BaseUseCase[EvaluarSolicitudInputDTO, SolicitudOutputDTO]):
    def __init__(
        self,
        solicitud_repository: SolicitudRepository,
        empleado_repository: EmpleadoRepository,
        auditoria_use_case,
        notificacion_use_case,
    ):
        self._solicitud_repository = solicitud_repository
        self._empleado_repository = empleado_repository
        self._auditoria_use_case = auditoria_use_case
        self._notificacion_use_case = notificacion_use_case

    def execute(self, input_dto: EvaluarSolicitudInputDTO) -> SolicitudOutputDTO:
        solicitud = self._solicitud_repository.get_by_id(input_dto.solicitud_id)
        if not solicitud or solicitud.empresa_id != input_dto.empresa_id:
            raise SolicitudNoEncontradaException(str(input_dto.solicitud_id))

        solicitud.enviar_a_revision()
        solicitud.aprobar(input_dto.evaluado_por_id, input_dto.comentario)
        solicitud = self._solicitud_repository.save(solicitud)

        empleado = self._empleado_repository.get_by_id(solicitud.empleado_id)
        empleado_nombre = empleado.nombre_completo() if empleado else ""

        self._notificacion_use_case.notificar_resultado_solicitud(
            empresa_id=input_dto.empresa_id,
            empleado_id=solicitud.empleado_id,
            tipo_permiso=solicitud.tipo_permiso_nombre,
            resultado="aprobada",
            comentario=input_dto.comentario,
        )
        self._auditoria_use_case.registrar(
            empresa_id=input_dto.empresa_id,
            usuario_id=input_dto.evaluado_por_id,
            tipo_evento=TiposEvento.APROBACION_SOLICITUD,
            descripcion=f"Solicitud {solicitud.id} aprobada.",
            ip_address=None,
            detalles={"solicitud_id": solicitud.id},
        )

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