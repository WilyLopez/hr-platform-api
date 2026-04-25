from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any
from modules.auditoria.domain.exceptions import ModificacionAuditoriaException


@dataclass(frozen=True)
class RegistroAuditoria:
    id: Optional[int]
    empresa_id: Optional[int]
    usuario_id: Optional[int]
    rol_usuario: Optional[str]
    tipo_evento: str
    descripcion: str
    ip_address: Optional[str]
    detalles: Dict[str, Any]
    timestamp: datetime

    def intentar_modificar(self) -> None:
        raise ModificacionAuditoriaException()

    def intentar_eliminar(self) -> None:
        raise ModificacionAuditoriaException()