from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class GenerarQrInputDTO:
    empresa_id: int
    sede_id: int
    minutos_vigencia: Optional[int]


@dataclass
class QrOutputDTO:
    token: str
    sede_id: int
    sede_nombre: str
    expira_en: datetime
    imagen_base64: str