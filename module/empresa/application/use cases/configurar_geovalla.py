from shared.application.base_use_case import BaseUseCase
from shared.domain.value_objects import Coordenadas, RadioMetros
from modules.empresa.domain.repositories.sede_repository import SedeRepository
from modules.empresa.domain.exceptions import SedeNoEncontradaException
from modules.empresa.application.dtos.sede_dto import ActualizarSedeInputDTO, SedeOutputDTO


class ConfigurarGeovallaUseCase(BaseUseCase[ActualizarSedeInputDTO, SedeOutputDTO]):
    def __init__(self, sede_repository: SedeRepository):
        self._sede_repository = sede_repository

    def execute(self, input_dto: ActualizarSedeInputDTO) -> SedeOutputDTO:
        sede = self._sede_repository.get_by_id(input_dto.sede_id)
        if not sede or sede.empresa_id != input_dto.empresa_id:
            raise SedeNoEncontradaException(str(input_dto.sede_id))

        sede.actualizar(
            nombre=input_dto.nombre,
            direccion=input_dto.direccion,
            coordenadas=Coordenadas(input_dto.latitud, input_dto.longitud),
            radio_metros=RadioMetros(input_dto.radio_metros),
        )

        sede = self._sede_repository.save(sede)

        return SedeOutputDTO(
            id=sede.id,
            empresa_id=sede.empresa_id,
            nombre=sede.nombre,
            direccion=sede.direccion,
            latitud=sede.coordenadas.latitud,
            longitud=sede.coordenadas.longitud,
            radio_metros=sede.radio_metros.value,
            es_activa=sede.es_activa,
        )