from datetime import datetime
from shared.application.base_use_case import BaseUseCase
from shared.constants import MetodosMarcaje, TiposEvento
from modules.asistencia.domain.entities.registro_asistencia import RegistroAsistencia
from modules.asistencia.domain.repositories.asistencia_repository import AsistenciaRepository
from modules.empleado.domain.repositories.empleado_repository import EmpleadoRepository
from modules.empleado.domain.exceptions import EmpleadoNoEncontradoException
from modules.asistencia.application.dtos.asistencia_dto import RegistrarManualInputDTO, RegistroAsistenciaOutputDTO


class RegistrarManualUseCase(BaseUseCase[RegistrarManualInputDTO, RegistroAsistenciaOutputDTO]):
    def __init__(
        self,
        asistencia_repository: AsistenciaRepository,
        empleado_repository: EmpleadoRepository,
        auditoria_use_case,
    ):
        self._asistencia_repository = asistencia_repository
        self._empleado_repository = empleado_repository
        self._auditoria_use_case = auditoria_use_case

    def execute(self, input_dto: RegistrarManualInputDTO) -> RegistroAsistenciaOutputDTO:
        empleado = self._empleado_repository.get_by_id(input_dto.empleado_id)
        if not empleado or empleado.empresa_id != input_dto.empresa_id:
            raise EmpleadoNoEncontradoException(str(input_dto.empleado_id))

        hora = datetime.strptime(input_dto.hora, "%H:%M").time()
        timestamp = datetime.combine(input_dto.fecha, hora)

        registro = RegistroAsistencia(
            id=None,
            empresa_id=input_dto.empresa_id,
            empleado_id=input_dto.empleado_id,
            sede_id=empleado.sede_id,
            tipo=input_dto.tipo,
            metodo=MetodosMarcaje.MANUAL,
            coordenadas=None,
            es_tardanza=False,
            es_manual=True,
            justificacion_manual=input_dto.justificacion,
            timestamp=timestamp,
            fecha_creacion=datetime.now(),
        )
        registro = self._asistencia_repository.save(registro)

        self._auditoria_use_case.registrar(
            empresa_id=input_dto.empresa_id,
            usuario_id=input_dto.admin_id,
            tipo_evento=TiposEvento.REGISTRO_MANUAL,
            descripcion=f"Registro manual de {input_dto.tipo.lower()} para empleado {empleado.nombre_completo()}.",
            ip_address=None,
            detalles={"justificacion": input_dto.justificacion},
        )

        return RegistroAsistenciaOutputDTO(
            id=registro.id,
            empleado_id=registro.empleado_id,
            empleado_nombre=empleado.nombre_completo(),
            sede_id=registro.sede_id,
            sede_nombre=None,
            tipo=registro.tipo,
            metodo=registro.metodo,
            es_tardanza=registro.es_tardanza,
            es_manual=registro.es_manual,
            timestamp=registro.timestamp,
        )