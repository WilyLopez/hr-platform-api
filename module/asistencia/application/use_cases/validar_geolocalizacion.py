from shared.application.base_use_case import BaseUseCase
from modules.asistencia.domain.exceptions import FueraDeGeovallaException


class ValidarGeolocalizacionUseCase(BaseUseCase[dict, None]):
    def __init__(self, geolocalizacion_service):
        self._geolocalizacion_service = geolocalizacion_service

    def execute(self, input_dto: dict) -> None:
        distancia = self._geolocalizacion_service.calcular_distancia(
            lat1=input_dto["latitud_empleado"],
            lon1=input_dto["longitud_empleado"],
            lat2=input_dto["latitud_sede"],
            lon2=input_dto["longitud_sede"],
        )
        radio = input_dto["radio_metros"]
        if distancia > radio:
            raise FueraDeGeovallaException(distancia, radio)