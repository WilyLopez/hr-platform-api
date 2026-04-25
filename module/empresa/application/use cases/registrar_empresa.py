from datetime import datetime
from shared.application.base_use_case import BaseUseCase
from shared.domain.value_objects import Email, Ruc
from shared.constants import EstadosEmpresa
from modules.empresa.domain.entities.empresa import Empresa
from modules.empresa.domain.repositories.empresa_repository import EmpresaRepository
from modules.empresa.domain.exceptions import EmpresaYaRegistradaException
from modules.empresa.application.dtos.empresa_dto import RegistrarEmpresaInputDTO, EmpresaOutputDTO


class RegistrarEmpresaUseCase(BaseUseCase[RegistrarEmpresaInputDTO, EmpresaOutputDTO]):
    def __init__(
        self,
        empresa_repository: EmpresaRepository,
        sunat_service,
        usuario_use_case,
        suscripcion_use_case,
        auditoria_use_case,
        notificacion_use_case,
    ):
        self._empresa_repository = empresa_repository
        self._sunat_service = sunat_service
        self._usuario_use_case = usuario_use_case
        self._suscripcion_use_case = suscripcion_use_case
        self._auditoria_use_case = auditoria_use_case
        self._notificacion_use_case = notificacion_use_case

    def execute(self, input_dto: RegistrarEmpresaInputDTO) -> EmpresaOutputDTO:
        if self._empresa_repository.exists_by_ruc(input_dto.ruc):
            raise EmpresaYaRegistradaException(input_dto.ruc)

        datos_sunat = self._sunat_service.consultar_ruc(input_dto.ruc)

        empresa = Empresa(
            id=None,
            ruc=Ruc(input_dto.ruc),
            razon_social=datos_sunat["razon_social"],
            nombre_comercial=datos_sunat["razon_social"],
            correo=Email(input_dto.correo),
            telefono=input_dto.telefono,
            direccion=input_dto.direccion,
            logo_url=None,
            estado=EstadosEmpresa.EN_PRUEBA,
            fecha_registro=datetime.now(),
            fecha_actualizacion=None,
        )

        empresa = self._empresa_repository.save(empresa)

        self._usuario_use_case.crear_propietario(empresa.id, input_dto.correo, input_dto.contrasena)
        self._suscripcion_use_case.activar_trial(empresa.id, input_dto.plan_id)
        self._notificacion_use_case.notificar_registro_empresa(input_dto.correo, empresa)

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