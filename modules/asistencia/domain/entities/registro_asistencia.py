from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from shared.domain.value_objects import Coordenadas
from shared.constants import TiposMarcaje, OrigenMarcaje, EstadosAuditoriaMarcaje, ResultadosMarcaje, EstadosHorasExtras


@dataclass
class RegistroAsistencia:
    id: Optional[int]
    empresa_id: int
    empleado_id: int
    sede_id: int
    tipo: str
    origen: str
    coordenadas: Optional[Coordenadas]
    estado_auditoria: str
    resultado: str
    minutos_tardanza: int
    minutos_extra: int
    minutos_temprano: int
    horas_trabajadas: float
    nivel_confianza: int
    estado_extras: str
    minutos_extra_aprobados: int
    enviado_a_nomina: bool
    extras_evaluado_por_id: Optional[int]
    extras_fecha_evaluacion: Optional[datetime]
    extras_comentario: Optional[str]
    observaciones: Optional[str]
    timestamp: datetime
    fecha_creacion: datetime

    def __post_init__(self):
        if self.tipo not in {TiposMarcaje.ENTRADA, TiposMarcaje.SALIDA, TiposMarcaje.INICIO_REFRIGERIO, TiposMarcaje.FIN_REFRIGERIO}:
            raise ValueError(f"Tipo de marcaje inválido: {self.tipo}")
        if self.origen not in {OrigenMarcaje.QR, OrigenMarcaje.MANUAL, OrigenMarcaje.WEB, OrigenMarcaje.MOVIL, OrigenMarcaje.API}:
            raise ValueError(f"Origen de marcaje inválido: {self.origen}")
        if self.estado_auditoria not in dict(EstadosAuditoriaMarcaje.CHOICES):
            raise ValueError(f"Estado auditoría inválido: {self.estado_auditoria}")
        if self.resultado not in dict(ResultadosMarcaje.CHOICES):
            raise ValueError(f"Resultado de marcaje inválido: {self.resultado}")
        if self.estado_extras not in dict(EstadosHorasExtras.CHOICES):
            raise ValueError(f"Estado de horas extras inválido: {self.estado_extras}")

    def es_entrada(self) -> bool:
        return self.tipo == TiposMarcaje.ENTRADA

    def es_salida(self) -> bool:
        return self.tipo == TiposMarcaje.SALIDA
