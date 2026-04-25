from shared.application.base_use_case import BaseUseCase
from modules.empleado.domain.repositories.empleado_repository import EmpleadoRepository
from modules.empleado.domain.exceptions import EmpleadoNoEncontradoException
from modules.empresa.domain.repositories.sede_repository import SedeRepository
from modules.empresa.domain.exceptions import SedeNoEncontradaException
from modules.empleado.application.dtos.empleado_dto import AsignarSedeInputDTO


class AsignarSedeUseCase(BaseUseCase[AsignarSedeInputDTO, None]):
    def __init__(self, empleado_repository: EmpleadoRepository, sede_repository: SedeRepository):
        self._empleado_repository = empleado_repository
        self._sede_repository = sede_repository

    def execute(self, input_dto: AsignarSedeInputDTO) -> None:
        empleado = self._empleado_repository.get_by_id(input_dto.empleado_id)
        if not empleado or empleado.empresa_id != input_dto.empresa_id:
            raise EmpleadoNoEncontradoException(str(input_dto.empleado_id))

        sede = self._sede_repository.get_by_id(input_dto.sede_id)
        if not sede or sede.empresa_id != input_dto.empresa_id:
            raise SedeNoEncontradaException(str(input_dto.sede_id))

        empleado.asignar_sede(input_dto.sede_id)
        self._empleado_repository.save(empleado)