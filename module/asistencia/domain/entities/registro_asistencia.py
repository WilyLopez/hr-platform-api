from dataclasses import dataclass
from datetime import datetime, time
from typing import Optional
from shared.domain.value_objects import Coordenadas
from shared.constants import TiposMarcaje, MetodosMarcaje


@dataclass
class RegistroAsistencia:
    id: Optional[int]
    empresa_id: int
    empleado_id: int
    sede_id: int
    tipo: str
    metodo: str
    coordenadas: Optional[Coordenadas]
    es_tardanza: bool
    es_manual: bool
    justificacion_manual: Optional[str]
    timestamp: datetime
    fecha_creacion: datetime

    def __post_init__(self):
        if self.tipo not in {TiposMarcaje.ENTRADA, TiposMarcaje.SALIDA}:
            raise ValueError(f"Tipo de marcaje inválido: {self.tipo}")
        if self.metodo not in {MetodosMarcaje.QR, MetodosMarcaje.MANUAL}:
            raise ValueError(f"Método de marcaje inválido: {self.metodo}")

    def es_entrada(self) -> bool:
        return self.tipo == TiposMarcaje.ENTRADA

    def es_salida(self) -> bool:
        return self.tipo == TiposMarcaje.SALIDA

    @classmethod
    def calcular_tardanza(cls, hora_marcaje: time, hora_entrada_esperada: time) -> bool:
        return hora_marcaje > hora_entrada_esperada