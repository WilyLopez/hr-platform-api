from dataclasses import dataclass, field
from datetime import datetime, time, date
from typing import Optional, List


@dataclass
class Turno:
    id: Optional[int]
    horario_id: Optional[int]
    dia_semana: int  # 0=Lunes, 6=Domingo
    hora_inicio: Optional[time]
    hora_fin: Optional[time]
    minutos_refrigerio: int = 0
    es_laborable: bool = True

    def __post_init__(self):
        if not 0 <= self.dia_semana <= 6:
            raise ValueError("El día de la semana debe estar entre 0 (Lunes) y 6 (Domingo).")
        if self.es_laborable and (self.hora_inicio is None or self.hora_fin is None):
            raise ValueError("Un turno laborable debe tener hora_inicio y hora_fin.")


@dataclass
class Horario:
    id: Optional[int]
    empresa_id: int
    nombre: str
    descripcion: Optional[str] = None
    es_activo: bool = True
    tolerancia_ingreso_min: int = 15
    tolerancia_salida_min: int = 0
    horas_extras_permitidas: bool = False
    max_horas_extras_dia: int = 0
    
    fecha_creacion: datetime = field(default_factory=datetime.now)
    fecha_actualizacion: Optional[datetime] = None

    turnos: List[Turno] = field(default_factory=list)

    def agregar_turno(self, turno: Turno) -> None:
        if any(t.dia_semana == turno.dia_semana for t in self.turnos):
            raise ValueError(f"Ya existe un turno para el día {turno.dia_semana}.")
        self.turnos.append(turno)

    def desactivar(self) -> None:
        self.es_activo = False
        self.fecha_actualizacion = datetime.now()


@dataclass
class AsignacionHorario:
    id: Optional[int]
    empleado_id: int
    horario_id: int
    fecha_desde: date
    fecha_hasta: Optional[date] = None
    fecha_creacion: datetime = field(default_factory=datetime.now)
    creado_por_id: Optional[int] = None

    def __post_init__(self):
        if self.fecha_hasta and self.fecha_desde > self.fecha_hasta:
            raise ValueError("La fecha_desde no puede ser mayor a fecha_hasta.")


@dataclass
class DiaEspecial:
    id: Optional[int]
    empresa_id: int
    nombre: str
    fecha: date
    es_laborable: bool = False
    hora_inicio: Optional[time] = None
    hora_fin: Optional[time] = None
    
    def __post_init__(self):
        if self.es_laborable and (self.hora_inicio is None or self.hora_fin is None):
            raise ValueError("Un día especial laborable debe tener hora_inicio y hora_fin.")
