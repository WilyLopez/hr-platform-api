from shared.application.base_use_case import BaseUseCase
from shared.domain.value_objects import Email
from shared.constants import TiposEvento
from modules.empleado.domain.repositories.empleado_repository import EmpleadoRepository
from modules.empleado.domain.exceptions import EmpleadoNoEncontradoException
from modules.empleado.application.dtos.empleado_dto import ActualizarEmpleadoInputDTO, EmpleadoOutputDTO


class ActualizarEmpleadoUseCase(BaseUseCase[ActualizarEmpleadoInputDTO, EmpleadoOutputDTO]):
    def __init__(self, empleado_repository: EmpleadoRepository, auditoria_use_case):
        self._empleado_repository = empleado_repository
        self._auditoria_use_case = auditoria_use_case

    def execute(self, input_dto: ActualizarEmpleadoInputDTO) -> EmpleadoOutputDTO:
        empleado = self._empleado_repository.get_by_id(input_dto.empleado_id)
        if not empleado or empleado.empresa_id != input_dto.empresa_id:
            raise EmpleadoNoEncontradoException(str(input_dto.empleado_id))

        empleado.actualizar(
            nombres=input_dto.nombres,
            apellidos=input_dto.apellidos,
            correo=Email(input_dto.correo),
            cargo=input_dto.cargo,
            area=input_dto.area,
        )
        empleado = self._empleado_repository.save(empleado)

        self._auditoria_use_case.registrar(
            empresa_id=input_dto.empresa_id,
            usuario_id=None,
            tipo_evento=TiposEvento.MODIFICACION_EMPLEADO,
            descripcion=f"Empleado {empleado.nombre_completo()} actualizado.",
            ip_address=None,
            detalles={"empleado_id": empleado.id},
        )

        return EmpleadoOutputDTO(
            id=empleado.id,
            empresa_id=empleado.empresa_id,
            codigo_unico=str(empleado.codigo_unico),
            nombres=empleado.nombres,
            apellidos=empleado.apellidos,
            tipo_documento=empleado.documento.tipo,
            numero_documento=empleado.documento.value,
            correo=str(empleado.correo),
            cargo=empleado.cargo,
            area=empleado.area,
            sede_id=empleado.sede_id,
            sede_nombre=None,
            estado=empleado.estado,
            fecha_ingreso=empleado.fecha_ingreso,
            fecha_creacion=empleado.fecha_creacion,
        )