import secrets
import hashlib
from datetime import timedelta
from django.utils import timezone
from shared.application.base_use_case import BaseUseCase
from modules.asistencia.domain.entities.token_qr import TokenQr
from modules.asistencia.domain.repositories.qr_repository import QrRepository
from modules.empresa.domain.repositories.sede_repository import SedeRepository
from django.conf import settings


class GenerarTokenQrUseCase(BaseUseCase[int, str]):
    def __init__(
        self,
        qr_repository: QrRepository,
        sede_repository: SedeRepository,
    ):
        self._qr_repository = qr_repository
        self._sede_repository = sede_repository

    def execute(self, sede_id: int) -> str:
        sede = self._sede_repository.get_by_id(sede_id)
        if not sede:
            raise ValueError("Sede no encontrada.")

        # Generar token y nonce aleatorio
        token = secrets.token_hex(32)
        nonce = secrets.token_hex(16)
        
        # Firma para evitar clonación (token + nonce + secret_key)
        secret_key = getattr(settings, 'SECRET_KEY', 'default_secret')
        data_to_sign = f"{token}:{nonce}:{sede_id}:{sede.empresa_id}:{secret_key}"
        firma = hashlib.sha256(data_to_sign.encode('utf-8')).hexdigest()

        # Desactivar QRs anteriores de la sede
        self._qr_repository.desactivar_por_sede(sede_id)

        # Crear nuevo QR (vigencia de 30 segundos)
        ahora = timezone.now()
        expira_en = ahora + timedelta(seconds=30)

        token_qr = TokenQr(
            id=None,
            empresa_id=sede.empresa_id,
            sede_id=sede_id,
            token=token,
            nonce=nonce,
            firma=firma,
            expira_en=expira_en,
            es_activo=True,
            fecha_creacion=ahora
        )

        self._qr_repository.save(token_qr)
        
        # El front end usará este string para generar la imagen QR
        return f"{token}:{nonce}:{firma}"
