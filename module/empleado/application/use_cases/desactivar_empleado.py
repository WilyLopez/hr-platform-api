from shared.application.base_use_case import BaseUseCase
from modules.empleado.domain.repositories.empleado_repository import EmpleadoRepository
from modules.empleado.domain.exceptions import EmpleadoNoEncontradoException


class DesactivarEmpleadoUseCase(BaseUseCase[dict, None]):
    def __init__(self, empleado_repository: EmpleadoRepository, suscripcion_use_case):
        self._empleado_repository = empleado_repository
        self._suscripcion_use_case = suscripcion_use_case

    def execute(self, input_dto: dict) -> None:
        empleado = self._empleado_repository.get_by_id(input_dto["empleado_id"])
        if not empleado or empleado.empresa_id != input_dto["empresa_id"]:
            raise EmpleadoNoEncontradoException(str(input_dto["empleado_id"]))
        empleado.desactivar()
        self._empleado_repository.save(empleado)
        self._suscripcion_use_case.decrementar_usuario(input_dto["empresa_id"])