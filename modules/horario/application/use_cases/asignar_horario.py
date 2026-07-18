from datetime import date
from shared.application.base_use_case import BaseUseCase
from shared.domain.exceptions import EntityNotFoundException, BusinessRuleViolationException
from modules.horario.domain.entities.horario import AsignacionHorario
from modules.horario.domain.repositories.horario_repository import HorarioRepository, AsignacionHorarioRepository
from modules.empleado.domain.repositories.empleado_repository import EmpleadoRepository
from modules.horario.application.dtos.asignacion_dto import AsignarHorarioInputDTO, AsignacionOutputDTO

class FechasTraslapadasException(BusinessRuleViolationException):
    def __init__(self):
        super().__init__(
            message="El empleado ya tiene un horario asignado que se cruza con estas fechas.",
            code="fechas_traslapadas"
        )


class AsignarHorarioUseCase(BaseUseCase[AsignarHorarioInputDTO, AsignacionOutputDTO]):
    def __init__(
        self,
        asignacion_repository: AsignacionHorarioRepository,
        horario_repository: HorarioRepository,
        empleado_repository: EmpleadoRepository
    ):
        self._asignacion_repository = asignacion_repository
        self._horario_repository = horario_repository
        self._empleado_repository = empleado_repository

    def execute(self, input_dto: AsignarHorarioInputDTO) -> AsignacionOutputDTO:
        # 1. Validar que exista el empleado y pertenezca a la empresa
        empleado = self._empleado_repository.get_by_id(input_dto.empleado_id)
        if not empleado or empleado.empresa_id != input_dto.empresa_id:
            raise EntityNotFoundException("Empleado", str(input_dto.empleado_id))

        # 2. Validar que exista el horario y pertenezca a la empresa
        horario = self._horario_repository.get_horario_by_id(input_dto.horario_id)
        if not horario or horario.empresa_id != input_dto.empresa_id:
            raise EntityNotFoundException("Horario", str(input_dto.horario_id))

        # 3. Cerrar asignación anterior si es necesario (manejo del historial)
        # Buscar asignaciones actuales que no tengan fecha_hasta o que terminen después de fecha_desde
        asignaciones = self._asignacion_repository.get_asignaciones_by_empleado(input_dto.empleado_id)
        
        # Validación básica de traslape o cierre automático
        # Si hay una asignación activa sin fecha_hasta, y la nueva empieza después, cerramos la anterior.
        # Si se cruzan de manera compleja (ej. insertar en medio), lanzamos error para simplificar por ahora.
        for asig in asignaciones:
            if asig.fecha_hasta is None:
                if input_dto.fecha_desde > asig.fecha_desde:
                    # Cerrar asignación abierta un día antes de la nueva
                    from datetime import timedelta
                    asig.fecha_hasta = input_dto.fecha_desde - timedelta(days=1)
                    self._asignacion_repository.save_asignacion(asig)
                else:
                    raise FechasTraslapadasException()
            else:
                # Comprobar traslape: (StartA <= EndB) and (EndA >= StartB)
                nueva_fin = input_dto.fecha_hasta or date.max
                if (asig.fecha_desde <= nueva_fin) and (asig.fecha_hasta >= input_dto.fecha_desde):
                    raise FechasTraslapadasException()

        # 4. Crear nueva asignación
        nueva_asignacion = AsignacionHorario(
            id=None,
            empleado_id=input_dto.empleado_id,
            horario_id=input_dto.horario_id,
            fecha_desde=input_dto.fecha_desde,
            fecha_hasta=input_dto.fecha_hasta,
            creado_por_id=input_dto.creado_por_id
        )
        
        nueva_asignacion = self._asignacion_repository.save_asignacion(nueva_asignacion)

        return AsignacionOutputDTO(
            id=nueva_asignacion.id,
            empleado_id=nueva_asignacion.empleado_id,
            horario_id=nueva_asignacion.horario_id,
            horario_nombre=horario.nombre,
            fecha_desde=nueva_asignacion.fecha_desde,
            fecha_hasta=nueva_asignacion.fecha_hasta,
            fecha_creacion=nueva_asignacion.fecha_creacion
        )
