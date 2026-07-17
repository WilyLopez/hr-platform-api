from datetime import date, time
from typing import Optional, Tuple
from modules.solicitud.domain.repositories.solicitud_repository import SolicitudRepository
from modules.horario.domain.repositories.horario_repository import AsignacionHorarioRepository, TurnoRepository
from shared.constants import EstadosAsistenciaHoy

class DisponibilidadLaboralService:
    def __init__(
        self,
        solicitud_repository: SolicitudRepository,
        asignacion_repository: AsignacionHorarioRepository,
        turno_repository: TurnoRepository,
    ):
        self._solicitud_repository = solicitud_repository
        self._asignacion_repository = asignacion_repository
        self._turno_repository = turno_repository

    def evaluar_disponibilidad(
        self, empleado_id: int, fecha: date, hora_actual: Optional[time] = None
    ) -> Tuple[bool, str, Optional[str]]:
        """
        Evalúa si el empleado puede marcar asistencia en la fecha y hora indicadas.
        Retorna:
        - bool: True si puede marcar (o no está bloqueado por un permiso).
        - str: Estado de disponibilidad (EstadosAsistenciaHoy).
        - str: Nombre del permiso o justificación (si aplica).
        """
        # 1. Verificar si tiene horario (Esto se hace en el caso de uso normalmente, pero para el estado visual podemos asumirlo o simplemente revisar permisos)
        
        # 2. Verificar permisos aprobados
        solicitudes = self._solicitud_repository.get_aprobadas_en_periodo(empleado_id, fecha, fecha)
        
        if not solicitudes:
            return True, EstadosAsistenciaHoy.SIN_MARCAR, None

        # Asumimos que solo hay una solicitud relevante para el día o tomamos la primera
        solicitud = solicitudes[0]
        nombre_permiso = solicitud.tipo_permiso_nombre
        
        # Verificar permiso parcial
        if hora_actual and solicitud.hora_inicio and solicitud.hora_fin:
            # Si la hora actual está dentro del bloque del permiso
            if solicitud.hora_inicio <= hora_actual <= solicitud.hora_fin:
                return False, EstadosAsistenciaHoy.DE_PERMISO, nombre_permiso
            else:
                # Está fuera del permiso, puede marcar
                return True, EstadosAsistenciaHoy.SIN_MARCAR, f"{nombre_permiso} Parcial"
        else:
            # Permiso de día completo
            es_vacaciones = "vacacion" in nombre_permiso.lower() or "vacación" in nombre_permiso.lower()
            estado = EstadosAsistenciaHoy.VACACIONES if es_vacaciones else EstadosAsistenciaHoy.DE_PERMISO
            return False, estado, nombre_permiso
