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
    expira_en: datetime
    es_activo: bool
    fecha_creacion: datetime

    @classmethod
    def crear(cls, empresa_id: int, sede_id: int, minutos_vigencia: int = QR_EXPIRY_DEFAULT_MINUTES) -> "TokenQr":
        from datetime import timedelta
        ahora = datetime.now()
        return cls(
            id=None,
            empresa_id=empresa_id,
            sede_id=sede_id,
            token=uuid.uuid4().hex,
            expira_en=ahora + timedelta(minutes=minutos_vigencia),
            es_activo=True,
            fecha_creacion=ahora,
        )

    def esta_vigente(self) -> bool:
        return self.es_activo and datetime.now() < self.expira_en

    def verificar_vigencia(self) -> None:
        if not self.esta_vigente():
            raise QrVencidoException()

    def verificar_sede(self, sede_id_empleado: int) -> None:
        if self.sede_id != sede_id_empleado:
            raise QrSedeIncorrectaException()

    def invalidar(self) -> None:
        self.es_activo = False