from datetime import datetime
from shared.application.base_use_case import BaseUseCase
from modules.notificacion.domain.entities.notificacion import Notificacion
from modules.notificacion.domain.repositories.notificacion_repository import NotificacionRepository
from modules.notificacion.application.dtos.notificacion_dto import EnviarInAppInputDTO, NotificacionOutputDTO


class EnviarInAppUseCase(BaseUseCase[EnviarInAppInputDTO, NotificacionOutputDTO]):
    def __init__(self, notificacion_repository: NotificacionRepository, push_service):
        self._notificacion_repository = notificacion_repository
        self._push_service = push_service

    def execute(self, input_dto: EnviarInAppInputDTO) -> NotificacionOutputDTO:
        notificacion = Notificacion(
            id=None,
            empresa_id=input_dto.empresa_id,
            usuario_id=input_dto.usuario_id,
            titulo=input_dto.titulo,
            mensaje=input_dto.mensaje,
            canal=Notificacion.CANAL_IN_APP,
            leida=False,
            enviada=False,
            fecha_envio=None,
            fecha_lectura=None,
            fecha_creacion=datetime.now(),
        )

        notificacion.marcar_como_enviada()
        notificacion = self._notificacion_repository.save(notificacion)

        self._push_service.enviar_websocket(
            usuario_id=input_dto.usuario_id,
            titulo=input_dto.titulo,
            mensaje=input_dto.mensaje,
        )

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