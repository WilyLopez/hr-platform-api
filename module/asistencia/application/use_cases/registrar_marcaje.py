from datetime import datetime, date
from shared.application.base_use_case import BaseUseCase
from shared.domain.value_objects import Coordenadas
from shared.constants import TiposMarcaje, MetodosMarcaje, TiposEvento
from modules.asistencia.domain.entities.registro_asistencia import RegistroAsistencia
from modules.asistencia.domain.repositories.qr_repository import QrRepository
from modules.asistencia.domain.repositories.asistencia_repository import AsistenciaRepository
from modules.asistencia.domain.exceptions import MarcajeDuplicadoException, AsistenciaEnPermisoException
from modules.empleado.domain.repositories.empleado_repository import EmpleadoRepository
from modules.empleado.domain.exceptions import EmpleadoNoEncontradoException
from modules.empresa.domain.repositories.sede_repository import SedeRepository
from modules.solicitud.domain.repositories.solicitud_repository import SolicitudRepository
from modules.asistencia.application.use_cases.validar_geolocalizacion import ValidarGeolocalizacionUseCase
from modules.asistencia.application.dtos.asistencia_dto import RegistrarMarcajeInputDTO, RegistroAsistenciaOutputDTO


class RegistrarMarcajeUseCase(BaseUseCase[RegistrarMarcajeInputDTO, RegistroAsistenciaOutputDTO]):
    def __init__(
        self,
        asistencia_repository: AsistenciaRepository,
        qr_repository: QrRepository,
        empleado_repository: EmpleadoRepository,
        sede_repository: SedeRepository,
        solicitud_repository: SolicitudRepository,
        validar_geo_use_case: ValidarGeolocalizacionUseCase,
        auditoria_use_case,
    ):
        self._asistencia_repository = asistencia_repository
        self._qr_repository = qr_repository
        self._empleado_repository = empleado_repository
        self._sede_repository = sede_repository
        self._solicitud_repository = solicitud_repository
        self._validar_geo_use_case = validar_geo_use_case
        self._auditoria_use_case = auditoria_use_case

    def execute(self, input_dto: RegistrarMarcajeInputDTO) -> RegistroAsistenciaOutputDTO:
        empleado = self._empleado_repository.get_by_id(input_dto.empleado_id)
        if not empleado:
            raise EmpleadoNoEncontradoException(str(input_dto.empleado_id))
        empleado.verificar_esta_activo()

        token_qr = self._qr_repository.get_by_token(input_dto.token_qr)
        token_qr.verificar_vigencia()
        token_qr.verificar_sede(empleado.sede_id)

        sede = self._sede_repository.get_by_id(empleado.sede_id)

        self._validar_geo_use_case.execute({
            "latitud_empleado": input_dto.latitud,
            "longitud_empleado": input_dto.longitud,
            "latitud_sede": sede.coordenadas.latitud,
            "longitud_sede": sede.coordenadas.longitud,
            "radio_metros": sede.radio_metros.value,
        })

        hoy = date.today()
        solicitudes_aprobadas = self._solicitud_repository.get_aprobadas_en_periodo(
            empleado.id, hoy, hoy
        )
        if solicitudes_aprobadas:
            raise AsistenciaEnPermisoException()

        tipo = self._determinar_tipo(input_dto.empleado_id, hoy)

        if self._asistencia_repository.existe_marcaje_tipo_en_fecha(input_dto.empleado_id, tipo, hoy):
            raise MarcajeDuplicadoException(tipo)

        registro = RegistroAsistencia(
            id=None,
            empresa_id=input_dto.empresa_id,
            empleado_id=input_dto.empleado_id,
            sede_id=empleado.sede_id,
            tipo=tipo,
            metodo=MetodosMarcaje.QR,
            coordenadas=Coordenadas(input_dto.latitud, input_dto.longitud),
            es_tardanza=False,
            es_manual=False,
            justificacion_manual=None,
            timestamp=datetime.now(),
            fecha_creacion=datetime.now(),
        )

        registro = self._asistencia_repository.save(registro)

        self._auditoria_use_case.registrar(
            empresa_id=input_dto.empresa_id,
            usuario_id=empleado.usuario_id,
            tipo_evento=TiposEvento.REGISTRO_ASISTENCIA,
            descripcion=f"Marcaje de {tipo.lower()} registrado.",
            ip_address=None,
            detalles={"sede_id": empleado.sede_id, "metodo": MetodosMarcaje.QR},
        )

        return RegistroAsistenciaOutputDTO(
            id=registro.id,
            empleado_id=registro.empleado_id,
            empleado_nombre=empleado.nombre_completo(),
            sede_id=registro.sede_id,
            sede_nombre=sede.nombre,
            tipo=registro.tipo,
            metodo=registro.metodo,
            es_tardanza=registro.es_tardanza,
            es_manual=registro.es_manual,
            timestamp=registro.timestamp,
        )

    def _determinar_tipo(self, empleado_id: int, hoy: date) -> str:
        ultimo = self._asistencia_repository.get_ultimo_marcaje_del_dia(empleado_id, hoy)
        if not ultimo or ultimo.tipo == TiposMarcaje.SALIDA:
            return TiposMarcaje.ENTRADA
        return TiposMarcaje.SALIDA