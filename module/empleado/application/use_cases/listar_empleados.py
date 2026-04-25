from typing import List
from shared.application.base_use_case import BaseUseCase
from modules.empleado.domain.repositories.empleado_repository import EmpleadoRepository
from modules.empleado.application.dtos.empleado_dto import ListarEmpleadosInputDTO, EmpleadoOutputDTO


class ListarEmpleadosUseCase(BaseUseCase[ListarEmpleadosInputDTO, List[EmpleadoOutputDTO]]):
    def __init__(self, empleado_repository: EmpleadoRepository):
        self._empleado_repository = empleado_repository

    def execute(self, input_dto: ListarEmpleadosInputDTO) -> List[EmpleadoOutputDTO]:
        empleados = self._empleado_repository.get_by_empresa(
            empresa_id=input_dto.empresa_id,
            estado=input_dto.estado,
            area=input_dto.area,
            sede_id=input_dto.sede_id,
            search=input_dto.search,
            page=input_dto.page,
            page_size=input_dto.page_size,
        )
        return [
            EmpleadoOutputDTO(
                id=e.id,
                empresa_id=e.empresa_id,
                codigo_unico=str(e.codigo_unico),
                nombres=e.nombres,
                apellidos=e.apellidos,
                tipo_documento=e.documento.tipo,
                numero_documento=e.documento.value,
                correo=str(e.correo),
                cargo=e.cargo,
                area=e.area,
                sede_id=e.sede_id,
                sede_nombre=None,
                estado=e.estado,
                fecha_ingreso=e.fecha_ingreso,
                fecha_creacion=e.fecha_creacion,
            )
            for e in empleados
        ]