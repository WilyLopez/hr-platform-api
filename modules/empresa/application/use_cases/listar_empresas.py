from typing import List, Dict, Any, Optional
from shared.application.base_use_case import BaseUseCase
from modules.empresa.domain.repositories.empresa_repository import EmpresaRepository
from modules.suscripcion.domain.repositories.suscripcion_repository import SuscripcionRepository
from dataclasses import dataclass

@dataclass
class ListarEmpresasInputDTO:
    page: int
    page_size: int
    estado: Optional[str] = None

class ListarEmpresasUseCase(BaseUseCase[ListarEmpresasInputDTO, Dict[str, Any]]):
    def __init__(
        self,
        empresa_repository: EmpresaRepository,
        suscripcion_repository: SuscripcionRepository
    ):
        self._empresa_repository = empresa_repository
        self._suscripcion_repository = suscripcion_repository

    def execute(self, input_dto: ListarEmpresasInputDTO) -> Dict[str, Any]:
        empresas = self._empresa_repository.get_all(
            estado=input_dto.estado, 
            page=input_dto.page, 
            page_size=input_dto.page_size
        )
        total = self._empresa_repository.count_all(estado=input_dto.estado)

        results = []
        for emp in empresas:
            plan_nombre = None
            if self._suscripcion_repository:
                suscripcion = self._suscripcion_repository.get_by_empresa(emp.id)
                if suscripcion:
                    plan_nombre = suscripcion.plan_nombre

            results.append({
                "id": emp.id,
                "ruc": str(emp.ruc),
                "razon_social": emp.razon_social,
                "estado": emp.estado,
                "plan_nombre": plan_nombre,
                "fecha_registro": emp.fecha_registro
            })

        import math
        total_pages = math.ceil(total / input_dto.page_size) if input_dto.page_size > 0 else 1

        return {
            "results": results,
            "total": total,
            "page": input_dto.page,
            "page_size": input_dto.page_size,
            "total_pages": total_pages
        }
