from shared.application.base_use_case import BaseUseCase
from modules.empresa.domain.repositories.empresa_repository import EmpresaRepository
from modules.empresa.domain.exceptions import EmpresaNoEncontradaException
from modules.empresa.application.dtos.empresa_dto import ActualizarEmpresaInputDTO, EmpresaOutputDTO


class ActualizarEmpresaUseCase(BaseUseCase[ActualizarEmpresaInputDTO, EmpresaOutputDTO]):
    def __init__(self, empresa_repository: EmpresaRepository):
        self._empresa_repository = empresa_repository

    def execute(self, input_dto: ActualizarEmpresaInputDTO) -> EmpresaOutputDTO:
        empresa = self._empresa_repository.get_by_id(input_dto.empresa_id)
        if not empresa:
            raise EmpresaNoEncontradaException(str(input_dto.empresa_id))

        empresa.actualizar_perfil(
            nombre_comercial=input_dto.nombre_comercial,
            telefono=input_dto.telefono,
            direccion=input_dto.direccion,
            logo_url=input_dto.logo_url,
        )

        empresa = self._empresa_repository.save(empresa)

        return EmpresaOutputDTO(
            id=empresa.id,
            ruc=str(empresa.ruc),
            razon_social=empresa.razon_social,
            nombre_comercial=empresa.nombre_comercial,
            correo=str(empresa.correo),
            telefono=empresa.telefono,
            direccion=empresa.direccion,
            logo_url=empresa.logo_url,
            estado=empresa.estado,
            fecha_registro=empresa.fecha_registro,
        )