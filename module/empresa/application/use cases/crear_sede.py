from datetime import datetime
from shared.application.base_use_case import BaseUseCase
from shared.domain.value_objects import Coordenadas, RadioMetros
from modules.empresa.domain.entities.sede import Sede
from modules.empresa.domain.repositories.sede_repository import SedeRepository
from modules.empresa.domain.repositories.empresa_repository import EmpresaRepository
from modules.empresa.domain.exceptions import EmpresaNoEncontradaException
from modules.empresa.application.dtos.sede_dto import CrearSedeInputDTO, SedeOutputDTO


class CrearSedeUseCase(BaseUseCase[CrearSedeInputDTO, SedeOutputDTO]):
    def __init__(self, sede_repository: SedeRepository, empresa_repository: EmpresaRepository):
        self._sede_repository = sede_repository
        self._empresa_repository = empresa_repository

    def execute(self, input_dto: CrearSedeInputDTO) -> SedeOutputDTO:
        empresa = self._empresa_repository.get_by_id(input_dto.empresa_id)
        if not empresa:
            raise EmpresaNoEncontradaException(str(input_dto.empresa_id))

        sede = Sede(
            id=None,
            empresa_id=input_dto.empresa_id,
            nombre=input_dto.nombre,
            direccion=input_dto.direccion,
            coordenadas=Coordenadas(input_dto.latitud, input_dto.longitud),
            radio_metros=RadioMetros(input_dto.radio_metros),
            es_activa=True,
            fecha_creacion=datetime.now(),
            fecha_actualizacion=None,
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