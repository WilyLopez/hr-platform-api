from datetime import datetime
from shared.application.base_use_case import BaseUseCase
from modules.notificacion.domain.entities.notificacion import Notificacion
from modules.notificacion.domain.repositories.notificacion_repository import NotificacionRepository
from modules.notificacion.application.dtos.notificacion_dto import EnviarEmailInputDTO, NotificacionOutputDTO


class EnviarEmailUseCase(BaseUseCase[EnviarEmailInputDTO, NotificacionOutputDTO]):
    def __init__(self, notificacion_repository: NotificacionRepository, email_service):
        self._notificacion_repository = notificacion_repository
        self._email_service = email_service

    def execute(self, input_dto: EnviarEmailInputDTO) -> NotificacionOutputDTO:
        notificacion = Notificacion(
            id=None,
            empresa_id=input_dto.empresa_id,
            usuario_id=input_dto.usuario_id,
            titulo=input_dto.titulo,
            mensaje=input_dto.mensaje,
            canal=Notificacion.CANAL_EMAIL,
            leida=False,
            enviada=False,
            fecha_envio=None,
            fecha_lectura=None,
            fecha_creacion=datetime.now(),
        )

        self._email_service.enviar(
            destinatario=input_dto.correo_destino,
            asunto=input_dto.titulo,
            cuerpo=input_dto.mensaje,
        )
        notificacion.marcar_como_enviada()
        notificacion = self._notificacion_repository.save(notificacion)

        return NotificacionOutputDTO(
            id=notificacion.id,
            usuario_id=notificacion.usuario_id,
            titulo=notificacion.titulo,
            mensaje=notificacion.mensaje,
            canal=notificacion.canal,
            leida=notificacion.leida,
            enviada=notificacion.enviada,
            fecha_envio=notificacion.fecha_envio,
            fecha_creacion=notificacion.fecha_creacion,
        )