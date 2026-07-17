from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import uuid
from shared.constants import QR_EXPIRY_DEFAULT_MINUTES
from modules.asistencia.domain.exceptions import QrVencidoException, QrSedeIncorrectaException


@dataclass
class TokenQr:
    id: Optional[int]
    empresa_id: int
    sede_id: int
    token: str
    nonce: str
    firma: str
    expira_en: datetime
    es_activo: bool
    fecha_creacion: datetime

    @classmethod
    def crear(cls, empresa_id: int, sede_id: int, minutos_vigencia: int = QR_EXPIRY_DEFAULT_MINUTES) -> "TokenQr":
        from datetime import timedelta
        from django.utils import timezone
        import secrets
        import hashlib
        from django.conf import settings
        
        ahora = timezone.now()
        token = uuid.uuid4().hex
        nonce = secrets.token_hex(16)
        secret_key = getattr(settings, 'SECRET_KEY', 'default_secret')
        data_to_sign = f"{token}:{nonce}:{sede_id}:{empresa_id}:{secret_key}"
        firma = hashlib.sha256(data_to_sign.encode('utf-8')).hexdigest()

        return cls(
            id=None,
            empresa_id=empresa_id,
            sede_id=sede_id,
            token=token,
            nonce=nonce,
            firma=firma,
            expira_en=ahora + timedelta(minutes=minutos_vigencia),
            es_activo=True,
            fecha_creacion=ahora,
        )

    def esta_vigente(self) -> bool:
        from django.utils import timezone
        return self.es_activo and timezone.now() < self.expira_en

    def verificar_vigencia(self) -> None:
        if not self.esta_vigente():
            raise QrVencidoException()

    def verificar_sede(self, sede_id_empleado: int) -> None:
        if self.sede_id != sede_id_empleado:
            raise QrSedeIncorrectaException()

    def invalidar(self) -> None:
        self.es_activo = False