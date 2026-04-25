from shared.application.base_use_case import BaseUseCase
from shared.constants import QR_EXPIRY_DEFAULT_MINUTES
from modules.asistencia.domain.entities.token_qr import TokenQr
from modules.asistencia.domain.repositories.qr_repository import QrRepository
from modules.empresa.domain.repositories.sede_repository import SedeRepository
from modules.empresa.domain.exceptions import SedeNoEncontradaException
from modules.asistencia.application.dtos.qr_dto import GenerarQrInputDTO, QrOutputDTO


class GenerarQrUseCase(BaseUseCase[GenerarQrInputDTO, QrOutputDTO]):
    def __init__(
        self,
        qr_repository: QrRepository,
        sede_repository: SedeRepository,
        qr_generator_service,
    ):
        self._qr_repository = qr_repository
        self._sede_repository = sede_repository
        self._qr_generator_service = qr_generator_service

    def execute(self, input_dto: GenerarQrInputDTO) -> QrOutputDTO:
        sede = self._sede_repository.get_by_id(input_dto.sede_id)
        if not sede or sede.empresa_id != input_dto.empresa_id:
            raise SedeNoEncontradaException(str(input_dto.sede_id))

        self._qr_repository.invalidar_por_sede(input_dto.sede_id)

        minutos = input_dto.minutos_vigencia or QR_EXPIRY_DEFAULT_MINUTES
        token_qr = TokenQr.crear(input_dto.empresa_id, input_dto.sede_id, minutos)
        token_qr = self._qr_repository.save(token_qr)

        imagen_base64 = self._qr_generator_service.generar_imagen(token_qr.token)

        return QrOutputDTO(
            token=token_qr.token,
            sede_id=sede.id,
            sede_nombre=sede.nombre,
            expira_en=token_qr.expira_en,
            imagen_base64=imagen_base64,
        )