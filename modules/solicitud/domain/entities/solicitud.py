from dataclasses import dataclass
from datetime import date, datetime, time
from typing import Optional


@dataclass
class Solicitud:
    empresa_id: int
    empleado_id: int
    tipo_permiso_id: int
    tipo_permiso_nombre: str
    fecha_inicio: date
    fecha_fin: date
    motivo: str
    estado: str
    hora_inicio: Optional[time] = None
    hora_fin: Optional[time] = None
    id: Optional[int] = None
    adjunto_url: Optional[str] = None
    comentario_evaluador: Optional[str] = None
    evaluado_por_id: Optional[int] = None
    fecha_evaluacion: Optional[datetime] = None
    fecha_creacion: Optional[datetime] = None
    fecha_actualizacion: Optional[datetime] = None

    def aprobar(self, evaluado_por_id: int, comentario: str = '') -> None:
        self.estado = 'APROBADA'
        self.evaluado_por_id = evaluado_por_id
        self.comentario_evaluador = comentario
        self.fecha_evaluacion = datetime.now()
        self.fecha_actualizacion = datetime.now()

    def rechazar(self, evaluado_por_id: int, comentario: str) -> None:
        self.estado = 'RECHAZADA'
        self.evaluado_por_id = evaluado_por_id
        self.comentario_evaluador = comentario
        self.fecha_evaluacion = datetime.now()
        self.fecha_actualizacion = datetime.now()

    def cancelar(self) -> None:
        self.estado = 'CANCELADA'
        self.fecha_actualizacion = datetime.now()
        
    def dias_solicitados(self) -> int:
        return (self.fecha_fin - self.fecha_inicio).days + 1
