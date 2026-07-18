from shared.application.base_use_case import BaseUseCase
from shared.constants import TiposEvento, EstadosEmpresa
from modules.empresa.domain.repositories.empresa_repository import EmpresaRepository
from modules.empresa.domain.exceptions import EmpresaNoEncontradaException
from modules.empresa.domain.services.suspension_policy_service import SuspensionPolicyService, SuspensionPolicyResult
from shared.domain.exceptions import BusinessRuleViolationException


class SuspenderEmpresaUseCase(BaseUseCase[dict, None]):
    def __init__(self, empresa_repository: EmpresaRepository, suscripcion_repository, auditoria_use_case, email_service=None):
        self._empresa_repository = empresa_repository
        self._suscripcion_repository = suscripcion_repository
        self._auditoria_use_case = auditoria_use_case
        self._email_service = email_service

    def execute(self, input_dto: dict) -> None:
        empresa = self._empresa_repository.get_by_id(input_dto["empresa_id"])
        if not empresa:
            raise EmpresaNoEncontradaException(str(input_dto["empresa_id"]))

        # Obtener suscripcion activa
        suscripcion = self._suscripcion_repository.get_by_empresa(empresa.id)

        # 1. Aplicar politica de negocio de suspension
        politica = SuspensionPolicyService.evaluar(empresa.estado, suscripcion)
        if not politica.permitido:
            raise BusinessRuleViolationException(f"{politica.motivo} {politica.accion_requerida}")

        estado_anterior = empresa.estado
        plan_anterior = suscripcion.plan_nombre if suscripcion else "Básico"
        
        # 2. Suspender la empresa
        empresa.estado = EstadosEmpresa.SUSPENDIDA
        self._empresa_repository.save(empresa)

        # 3. Registrar auditoria con todos los detalles requeridos
        self._auditoria_use_case.registrar(
            empresa_id=empresa.id,
            usuario_id=input_dto["suspendido_por_id"],
            tipo_evento=TiposEvento.SUSPENSION_EMPRESA,
            descripcion=f"Empresa '{empresa.razon_social}' suspendida.",
            ip_address=input_dto.get("ip_address"),
            detalles={
                "estado_anterior": estado_anterior,
                "estado_nuevo": empresa.estado,
                "plan_anterior": plan_anterior,
                "motivo_categoria": input_dto.get("motivo_categoria", "OTRO"),
                "comentario": input_dto.get("comentario", "")
            },
        )

        # 4. Notificar al propietario de la empresa (si existe y tenemos su correo)
        if self._email_service and input_dto.get("propietario_email"):
            try:
                self._email_service.notificar_suspension_empresa(
                    correo=input_dto["propietario_email"],
                    empresa_nombre=empresa.razon_social,
                    motivo=input_dto.get("motivo_categoria", "Motivo no especificado")
                )
            except Exception:
                pass # Fallback silencioso si falla el correo, no bloqueamos la suspension