from datetime import datetime
from shared.application.base_use_case import BaseUseCase
from shared.domain.value_objects import Email, CodigoUnico, NumeroDocumento
from shared.constants import EstadosEmpleado, TiposEvento
from modules.empleado.domain.entities.empleado import Empleado
from modules.empleado.domain.repositories.empleado_repository import EmpleadoRepository
from modules.empleado.domain.exceptions import EmpleadoYaExisteException
from modules.empleado.application.dtos.empleado_dto import RegistrarEmpleadoInputDTO, EmpleadoOutputDTO


class RegistrarEmpleadoUseCase(BaseUseCase[RegistrarEmpleadoInputDTO, EmpleadoOutputDTO]):
    def __init__(
        self,
        empleado_repository: EmpleadoRepository,
        suscripcion_use_case,
        usuario_use_case,
        auditoria_use_case,
        notificacion_use_case,
    ):
        self._empleado_repository = empleado_repository
        self._suscripcion_use_case = suscripcion_use_case
        self._usuario_use_case = usuario_use_case
        self._auditoria_use_case = auditoria_use_case
        self._notificacion_use_case = notificacion_use_case

    def execute(self, input_dto: RegistrarEmpleadoInputDTO) -> EmpleadoOutputDTO:
        self._suscripcion_use_case.verificar_limites(input_dto.empresa_id)

        if self._empleado_repository.exists_by_documento(input_dto.empresa_id, input_dto.numero_documento):
            raise EmpleadoYaExisteException("número de documento", input_dto.numero_documento)

        if self._empleado_repository.exists_by_correo(input_dto.empresa_id, input_dto.correo):
            raise EmpleadoYaExisteException("correo", input_dto.correo)

        codigo_unico = self._generar_codigo_unico()
        usuario = self._usuario_use_case.crear_empleado(input_dto.empresa_id, input_dto.correo, codigo_unico)

        empleado = Empleado(
            id=None,
            empresa_id=input_dto.empresa_id,
            usuario_id=usuario.id,
            codigo_unico=codigo_unico,
            nombres=input_dto.nombres,
            apellidos=input_dto.apellidos,
            documento=NumeroDocumento(input_dto.numero_documento, input_dto.tipo_documento),
            correo=Email(input_dto.correo),
            cargo=input_dto.cargo,
            area=input_dto.area,
            sede_id=input_dto.sede_id,
            estado=EstadosEmpleado.ACTIVO,
            fecha_ingreso=input_dto.fecha_ingreso,
            fecha_creacion=datetime.now(),
            fecha_actualizacion=None,
        )

        empleado = self._empleado_repository.save(empleado)

        self._notificacion_use_case.notificar_bienvenida_empleado(
            correo=input_dto.correo,
            codigo_unico=str(codigo_unico),
        )
        self._auditoria_use_case.registrar(
            empresa_id=input_dto.empresa_id,
            usuario_id=None,
            tipo_evento=TiposEvento.CREACION_EMPLEADO,
            descripcion=f"Empleado {empleado.nombre_completo()} registrado.",
            ip_address=None,
            detalles={"empleado_id": empleado.id},
        )

        return self._to_output(empleado)

    def _generar_codigo_unico(self) -> CodigoUnico:
        while True:
            codigo = CodigoUnico.generate()
            if not self._empleado_repository.exists_by_codigo_unico(str(codigo)):
                return codigo

    def _to_output(self, empleado: Empleado) -> EmpleadoOutputDTO:
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