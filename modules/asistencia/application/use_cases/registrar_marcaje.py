from datetime import datetime, date, timedelta
from django.utils import timezone
from django.db import transaction
from shared.application.base_use_case import BaseUseCase
from shared.domain.value_objects import Coordenadas
from shared.constants import TiposMarcaje, OrigenMarcaje, TiposEvento, EstadosAuditoriaMarcaje, ResultadosMarcaje, EstadosHorasExtras
from modules.asistencia.domain.entities.registro_asistencia import RegistroAsistencia
from modules.asistencia.domain.repositories.qr_repository import QrRepository
from modules.asistencia.domain.repositories.asistencia_repository import AsistenciaRepository
from modules.asistencia.domain.exceptions import MarcajeDuplicadoException, AsistenciaEnPermisoException
from shared.domain.exceptions import InvalidValueException, BusinessRuleViolationException
from modules.empleado.domain.repositories.empleado_repository import EmpleadoRepository
from modules.empleado.domain.exceptions import EmpleadoNoEncontradoException
from modules.empresa.domain.repositories.sede_repository import SedeRepository
from modules.asistencia.domain.services.disponibilidad_laboral_service import DisponibilidadLaboralService
from modules.horario.domain.repositories.horario_repository import AsignacionHorarioRepository, TurnoRepository, HorarioRepository
from modules.asistencia.application.use_cases.validar_geolocalizacion import ValidarGeolocalizacionUseCase
from modules.asistencia.application.dtos.asistencia_dto import RegistrarMarcajeInputDTO, RegistroAsistenciaOutputDTO


class RegistrarMarcajeUseCase(BaseUseCase[RegistrarMarcajeInputDTO, RegistroAsistenciaOutputDTO]):
    def __init__(
        self,
        asistencia_repository: AsistenciaRepository,
        qr_repository: QrRepository,
        empleado_repository: EmpleadoRepository,
        sede_repository: SedeRepository,
        disponibilidad_service: DisponibilidadLaboralService,
        asignacion_repository: AsignacionHorarioRepository,
        horario_repository: HorarioRepository,
        turno_repository: TurnoRepository,
        validar_geo_use_case: ValidarGeolocalizacionUseCase,
        auditoria_use_case,
    ):
        self._asistencia_repository = asistencia_repository
        self._qr_repository = qr_repository
        self._empleado_repository = empleado_repository
        self._sede_repository = sede_repository
        self._disponibilidad_service = disponibilidad_service
        self._asignacion_repository = asignacion_repository
        self._horario_repository = horario_repository
        self._turno_repository = turno_repository
        self._validar_geo_use_case = validar_geo_use_case
        self._auditoria_use_case = auditoria_use_case

    def execute(self, input_dto: RegistrarMarcajeInputDTO) -> RegistroAsistenciaOutputDTO:
        with transaction.atomic():
            empleado = self._empleado_repository.get_by_usuario_id(input_dto.usuario_id)
            if not empleado:
                raise EmpleadoNoEncontradoException(f"usuario_id={input_dto.usuario_id}")
            empleado.verificar_esta_activo()

            if input_dto.origen == OrigenMarcaje.QR:
                if not input_dto.token_qr:
                    raise InvalidValueException("El token QR es obligatorio para este origen.")
                
                parts = input_dto.token_qr.split(":")
                if len(parts) != 3:
                    raise InvalidValueException("Formato de token QR inválido.")
                token, nonce, firma = parts
                
                token_qr = self._qr_repository.get_by_token(token)
                if not token_qr:
                    raise InvalidValueException("Token QR no encontrado.")
                    
                if token_qr.nonce != nonce or token_qr.firma != firma:
                    raise InvalidValueException("Firma de QR inválida.")
                    
                token_qr.verificar_vigencia()
                token_qr.verificar_sede(empleado.sede_id)

            sede = self._sede_repository.get_by_id(empleado.sede_id)

            if input_dto.latitud is not None and input_dto.longitud is not None:
                self._validar_geo_use_case.execute({
                    "latitud_empleado": input_dto.latitud,
                    "longitud_empleado": input_dto.longitud,
                    "latitud_sede": sede.coordenadas.latitud,
                    "longitud_sede": sede.coordenadas.longitud,
                    "radio_metros": sede.radio_metros.value,
                })

            hoy = timezone.localdate()
            now = timezone.localtime()

            puede_marcar, _, justificacion = self._disponibilidad_service.evaluar_disponibilidad(empleado.id, hoy, now.time())
            if not puede_marcar:
                raise AsistenciaEnPermisoException()

            # Find active schedule and today's shift
            asignacion = self._asignacion_repository.get_asignacion_activa(empleado.id, hoy)
            if not asignacion:
                raise BusinessRuleViolationException("El empleado no tiene un horario asignado para el día de hoy.")

            horario = self._horario_repository.get_horario_by_id(asignacion.horario_id)
            turnos = self._turno_repository.get_turnos_by_horario(horario.id)
            turno_hoy = next((t for t in turnos if t.dia_semana == hoy.weekday()), None)

            if not turno_hoy or not turno_hoy.es_laborable:
                # Can be "Fuera de Horario" or "Día Libre"
                tipo = TiposMarcaje.ENTRADA
                resultado = ResultadosMarcaje.FUERA_HORARIO
            else:
                # Fetch today's punches to determine next type
                marcajes_hoy = self._asistencia_repository.get_marcajes_del_dia(empleado.id, hoy)
                
                # Check for double punch within 1 minute
                if marcajes_hoy:
                    ultimo_marcaje = marcajes_hoy[-1]
                    if (now - ultimo_marcaje.timestamp).total_seconds() < 60:
                        raise BusinessRuleViolationException("Marcaje duplicado detectado. Por favor, espere 1 minuto.")

                # Determine next state
                tiene_refrigerio = turno_hoy.minutos_refrigerio > 0
                secuencia_esperada = [TiposMarcaje.ENTRADA, TiposMarcaje.SALIDA]
                if tiene_refrigerio:
                    secuencia_esperada = [TiposMarcaje.ENTRADA, TiposMarcaje.INICIO_REFRIGERIO, TiposMarcaje.FIN_REFRIGERIO, TiposMarcaje.SALIDA]

                if len(marcajes_hoy) >= len(secuencia_esperada):
                    tipo = TiposMarcaje.SALIDA # o Entrada Extra
                    resultado = ResultadosMarcaje.EXTRA
                else:
                    tipo = secuencia_esperada[len(marcajes_hoy)]
                    resultado = self._calcular_resultado(tipo, now, turno_hoy, horario)

            minutos_extra = 0
            minutos_tardanza = 0
            minutos_temprano = 0
            estado_extras = EstadosHorasExtras.NO_REQUIERE
            if resultado == ResultadosMarcaje.TARDE and tipo == TiposMarcaje.ENTRADA:
                esperado = datetime.combine(hoy, turno_hoy.hora_inicio)
                minutos_tardanza = int((now.replace(tzinfo=None) - esperado).total_seconds() / 60)
            elif tipo == TiposMarcaje.SALIDA:
                esperado = datetime.combine(hoy, turno_hoy.hora_fin)
                if resultado == ResultadosMarcaje.TEMPRANO:
                    minutos_temprano = int((esperado - now.replace(tzinfo=None)).total_seconds() / 60)
                else:
                    # Check for extra minutes
                    diff_seconds = (now.replace(tzinfo=None) - esperado).total_seconds()
                    if diff_seconds > 0:
                        minutos_extra = int(diff_seconds / 60)
                        if minutos_extra > 0:
                            estado_extras = EstadosHorasExtras.PENDIENTE

            registro = RegistroAsistencia(
                id=None,
                empresa_id=input_dto.empresa_id,
                empleado_id=empleado.id,
                sede_id=empleado.sede_id,
                tipo=tipo,
                origen=input_dto.origen,
                coordenadas=Coordenadas(input_dto.latitud, input_dto.longitud) if input_dto.latitud else None,
                estado_auditoria=EstadosAuditoriaMarcaje.VALIDO,
                resultado=resultado,
                minutos_tardanza=max(0, minutos_tardanza),
                minutos_extra=max(0, minutos_extra),
                minutos_temprano=max(0, minutos_temprano),
                horas_trabajadas=0.0,
                nivel_confianza=100,
                estado_extras=estado_extras,
                minutos_extra_aprobados=0,
                enviado_a_nomina=False,
                extras_evaluado_por_id=None,
                extras_fecha_evaluacion=None,
                extras_comentario=None,
                observaciones=None,
                timestamp=now,
                fecha_creacion=now,
            )

            registro = self._asistencia_repository.save(registro)

            self._auditoria_use_case.registrar(
                empresa_id=input_dto.empresa_id,
                usuario_id=empleado.usuario_id,
                tipo_evento=TiposEvento.REGISTRO_ASISTENCIA,
                descripcion=f"Marcaje de {tipo.lower()} registrado vía {input_dto.origen}.",
                ip_address=None,
                detalles={"sede_id": empleado.sede_id, "origen": input_dto.origen, "resultado": resultado},
            )

            return RegistroAsistenciaOutputDTO(
                id=registro.id,
                empleado_id=registro.empleado_id,
                empleado_nombre=empleado.nombre_completo(),
                sede_id=registro.sede_id,
                sede_nombre=sede.nombre,
                tipo=registro.tipo,
                origen=registro.origen,
                estado_auditoria=registro.estado_auditoria,
                resultado=registro.resultado,
                minutos_tardanza=registro.minutos_tardanza,
                minutos_extra=registro.minutos_extra,
                minutos_temprano=registro.minutos_temprano,
                horas_trabajadas=registro.horas_trabajadas,
                estado_extras=registro.estado_extras,
                timestamp=registro.timestamp,
            )

    def _calcular_resultado(self, tipo: str, now: datetime, turno, horario) -> str:
        hora_actual = now.time()
        if tipo == TiposMarcaje.ENTRADA:
            limite = (datetime.combine(date.today(), turno.hora_inicio) + timedelta(minutes=horario.tolerancia_ingreso_min)).time()
            if hora_actual <= limite:
                return ResultadosMarcaje.NORMAL
            return ResultadosMarcaje.TARDE
        elif tipo == TiposMarcaje.SALIDA:
            if hora_actual < turno.hora_fin:
                return ResultadosMarcaje.TEMPRANO
            return ResultadosMarcaje.NORMAL
        return ResultadosMarcaje.NORMAL
