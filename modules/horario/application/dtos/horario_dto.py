from dataclasses import dataclass
from typing import List, Optional
from datetime import time, date

@dataclass
class TurnoInputDTO:
    dia_semana: int
    hora_inicio: Optional[time]
    hora_fin: Optional[time]
    minutos_refrigerio: int = 0
    es_laborable: bool = True

@dataclass
class TurnoOutputDTO:
    id: int
    horario_id: int
    dia_semana: int
    hora_inicio: Optional[time]
    hora_fin: Optional[time]
    minutos_refrigerio: int
    es_laborable: bool

@dataclass
class CrearHorarioInputDTO:
    empresa_id: int
    nombre: str
    descripcion: Optional[str]
    tolerancia_ingreso_min: int
    tolerancia_salida_min: int
    horas_extras_permitidas: bool
    max_horas_extras_dia: int
    turnos: List[TurnoInputDTO]

@dataclass
class ActualizarHorarioInputDTO:
    horario_id: int
    empresa_id: int
    nombre: str
    descripcion: Optional[str]
    es_activo: bool
    tolerancia_ingreso_min: int
    tolerancia_salida_min: int
    horas_extras_permitidas: bool
    max_horas_extras_dia: int
    turnos: List[TurnoInputDTO]

@dataclass
class HorarioOutputDTO:
    id: int
    nombre: str
    descripcion: Optional[str]
    es_activo: bool
    tolerancia_ingreso_min: int
    tolerancia_salida_min: int
    horas_extras_permitidas: bool
    max_horas_extras_dia: int
    turnos: List[TurnoOutputDTO]
    empleados_asignados: Optional[int] = None
