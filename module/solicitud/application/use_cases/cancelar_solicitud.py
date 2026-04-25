from shared.application.base_use_case import BaseUseCase
from modules.solicitud.domain.repositories.solicitud_repository import SolicitudRepository
from modules.solicitud.domain.exceptions import (
    SolicitudNoEncontradaException,
    SolicitudNoPerteneceEmpleadoException,
)


class CancelarSolicitudUseCase(BaseUseCase[dict, None]):
    def __init__(self, solicitud_repository: SolicitudRepository):
        self._solicitud_repository = solicitud_repository

    def execute(self, input_dto: dict) -> None:
        solicitud = self._solicitud_repository.get_by_id(input_dto["solicitud_id"])
        if not solicitud or solicitud.empresa_id != input_dto["empresa_id"]:
            raise SolicitudNoEncontradaException(str(input_dto["solicitud_id"]))

        if solicitud.empleado_id != input_dto["empleado_id"]:
            raise SolicitudNoPerteneceEmpleadoException()

        solicitud.cancelar()
        self._solicitud_repository.save(solicitud)