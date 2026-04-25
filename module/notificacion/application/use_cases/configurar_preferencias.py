from shared.application.base_use_case import BaseUseCase
from modules.notificacion.application.dtos.notificacion_dto import ConfigurarPreferenciasInputDTO


class ConfigurarPreferenciasUseCase(BaseUseCase[ConfigurarPreferenciasInputDTO, None]):
    def __init__(self, preferencias_repository):
        self._preferencias_repository = preferencias_repository

    def execute(self, input_dto: ConfigurarPreferenciasInputDTO) -> None:
        self._preferencias_repository.guardar(
            usuario_id=input_dto.usuario_id,
            email_habilitado=input_dto.email_habilitado,
            push_habilitado=input_dto.push_habilitado,
        )