from shared.application.base_use_case import BaseUseCase
from shared.constants import TiposEvento


class CerrarSesionUseCase(BaseUseCase[dict, None]):
    def __init__(self, jwt_service, auditoria_use_case):
        self._jwt_service = jwt_service
        self._auditoria_use_case = auditoria_use_case

    def execute(self, input_dto: dict) -> None:
        self._jwt_service.invalidar_refresh_token(input_dto["refresh_token"])

        self._auditoria_use_case.registrar(
            empresa_id=input_dto.get("empresa_id"),
            usuario_id=input_dto["usuario_id"],
            tipo_evento=TiposEvento.CIERRE_SESION,
            descripcion="Cierre de sesión.",
            ip_address=input_dto.get("ip_address"),
            detalles={},
        )