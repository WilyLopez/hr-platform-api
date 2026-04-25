from shared.application.base_use_case import BaseUseCase
from shared.constants import TiposEvento
from modules.empresa.domain.repositories.empresa_repository import EmpresaRepository
from modules.empresa.domain.exceptions import EmpresaNoEncontradaException


class SuspenderEmpresaUseCase(BaseUseCase[dict, None]):
    def __init__(self, empresa_repository: EmpresaRepository, auditoria_use_case):
        self._empresa_repository = empresa_repository
        self._auditoria_use_case = auditoria_use_case

    def execute(self, input_dto: dict) -> None:
        empresa = self._empresa_repository.get_by_id(input_dto["empresa_id"])
        if not empresa:
            raise EmpresaNoEncontradaException(str(input_dto["empresa_id"]))

        empresa.suspender()
        self._empresa_repository.save(empresa)

        self._auditoria_use_case.registrar(
            empresa_id=empresa.id,
            usuario_id=input_dto["suspendido_por_id"],
            tipo_evento=TiposEvento.SUSPENSION_EMPRESA,
            descripcion=f"Empresa '{empresa.razon_social}' suspendida.",
            ip_address=input_dto.get("ip_address"),
            detalles={"razon": input_dto.get("razon", "")},
        )