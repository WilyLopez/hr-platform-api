from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from modules.asistencia.application.dtos.asistencia_dto import (
    RegistrarMarcajeInputDTO,
    RegistrarManualInputDTO,
    ListarAsistenciaInputDTO,
)
from modules.asistencia.interfaces.serializers.asistencia_serializer import (
    RegistrarMarcajeSerializer,
    RegistrarManualSerializer,
    RegistroAsistenciaOutputSerializer,
    ReporteAsistenciaOutputSerializer,
    EstadoAsistenciaHoySerializer,
)
from modules.asistencia.infrastructure.repositories.asistencia_repository_impl import DjangoAsistenciaRepository
from modules.asistencia.infrastructure.repositories.qr_repository_impl import DjangoQrRepository
from modules.empleado.infrastructure.repositories.empleado_repository_impl import DjangoEmpleadoRepository
from modules.empresa.infrastructure.repositories.sede_repository_impl import DjangoSedeRepository
from modules.solicitud.infrastructure.repositories.solicitud_repository_impl import DjangoSolicitudRepository
from modules.horario.infrastructure.repositories.horario_repository_impl import DjangoAsignacionHorarioRepository, DjangoHorarioRepository, DjangoTurnoRepository
from modules.asistencia.infrastructure.services.geolocalizacion_service import GeolocalizacionService
from modules.asistencia.application.use_cases.validar_geolocalizacion import ValidarGeolocalizacionUseCase
from modules.asistencia.application.use_cases.registrar_marcaje import RegistrarMarcajeUseCase
from modules.asistencia.application.use_cases.registrar_manual import RegistrarManualUseCase
from modules.asistencia.application.use_cases.generar_reporte import GenerarReporteAsistenciaUseCase
from modules.auditoria.infrastructure.repositories.auditoria_repository_impl import DjangoAuditoriaRepository
from modules.auditoria.application.use_cases.registrar_evento import RegistrarEventoUseCase
from modules.asistencia.application.use_cases.listar_asistencias import ListarAsistenciasUseCase
from modules.asistencia.application.use_cases.obtener_estado_asistencia_hoy import ObtenerEstadoAsistenciaHoyUseCase


def _auditoria():
    return RegistrarEventoUseCase(DjangoAuditoriaRepository())


class MarcajeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = RegistrarMarcajeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        d = serializer.validated_data
        from modules.asistencia.domain.services.disponibilidad_laboral_service import DisponibilidadLaboralService
        asignacion_repo = DjangoAsignacionHorarioRepository()
        horario_repo = DjangoHorarioRepository()
        turno_repo = DjangoTurnoRepository()
        
        disponibilidad_service = DisponibilidadLaboralService(
            asignacion_repository=asignacion_repo,
            turno_repository=turno_repo,
            solicitud_repository=DjangoSolicitudRepository()
        )

        use_case = RegistrarMarcajeUseCase(
            asistencia_repository=DjangoAsistenciaRepository(),
            qr_repository=DjangoQrRepository(),
            empleado_repository=DjangoEmpleadoRepository(),
            sede_repository=DjangoSedeRepository(),
            disponibilidad_service=disponibilidad_service,
            asignacion_repository=asignacion_repo,
            horario_repository=horario_repo,
            turno_repository=turno_repo,
            validar_geo_use_case=ValidarGeolocalizacionUseCase(GeolocalizacionService()),
            auditoria_use_case=_auditoria(),
        )
        output = use_case.execute(RegistrarMarcajeInputDTO(
            usuario_id=request.user.id,
            empresa_id=request.user.empresa_id,
            **d,
        ))
        return Response(RegistroAsistenciaOutputSerializer(output).data, status=status.HTTP_201_CREATED)


class EstadoAsistenciaHoyView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from modules.asistencia.domain.services.disponibilidad_laboral_service import DisponibilidadLaboralService
        
        asignacion_repo = DjangoAsignacionHorarioRepository()
        horario_repo = DjangoHorarioRepository()
        turno_repo = DjangoTurnoRepository()
        solicitud_repo = DjangoSolicitudRepository()
        
        disponibilidad_service = DisponibilidadLaboralService(
            asignacion_repository=asignacion_repo,
            turno_repository=turno_repo,
            solicitud_repository=solicitud_repo
        )

        use_case = ObtenerEstadoAsistenciaHoyUseCase(
            asistencia_repository=DjangoAsistenciaRepository(),
            asignacion_repository=asignacion_repo,
            horario_repository=horario_repo,
            turno_repository=turno_repo,
            empleado_repository=DjangoEmpleadoRepository(),
            disponibilidad_service=disponibilidad_service
        )
        output = use_case.execute(request.user.id)
        return Response(EstadoAsistenciaHoySerializer(output).data)


class AsistenciaManualView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = RegistrarManualSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        d = serializer.validated_data
        use_case = RegistrarManualUseCase(
            asistencia_repository=DjangoAsistenciaRepository(),
            empleado_repository=DjangoEmpleadoRepository(),
            auditoria_use_case=_auditoria(),
        )
        output = use_case.execute(RegistrarManualInputDTO(
            empresa_id=request.user.empresa_id,
            admin_id=request.user.id,
            **d,
        ))
        return Response(RegistroAsistenciaOutputSerializer(output).data, status=status.HTTP_201_CREATED)


class ReporteAsistenciaView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from datetime import date
        qp = request.query_params
        input_dto = ListarAsistenciaInputDTO(
            empresa_id=request.user.empresa_id,
            empleado_id=int(qp["empleado_id"]) if qp.get("empleado_id") else None,
            emerald_id=int(qp["sede_id"]) if qp.get("sede_id") else None,
            area=qp.get("area"),
            fecha_desde=date.fromisoformat(qp["fecha_desde"]) if qp.get("fecha_desde") else None,
            fecha_hasta=date.fromisoformat(qp["fecha_hasta"]) if qp.get("fecha_hasta") else None,
        )
        use_case = GenerarReporteAsistenciaUseCase(
            DjangoAsistenciaRepository(), DjangoEmpleadoRepository(), DjangoSedeRepository()
        )
        output = use_case.execute(input_dto)
        return Response(ReporteAsistenciaOutputSerializer(output).data)
class AsistenciaListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from datetime import date
        qp = request.query_params
        
        fecha_param = qp.get("fecha")
        f_desde = date.fromisoformat(fecha_param) if fecha_param else None
        f_hasta = date.fromisoformat(fecha_param) if fecha_param else None

        if qp.get("fecha_desde"):
            f_desde = date.fromisoformat(qp["fecha_desde"])
        if qp.get("fecha_hasta"):
            f_hasta = date.fromisoformat(qp["fecha_hasta"])

        input_dto = ListarAsistenciaInputDTO(
            empresa_id=request.user.empresa_id,
            empleado_id=int(qp["empleado_id"]) if qp.get("empleado_id") else None,
            sede_id=int(qp["sede_id"]) if qp.get("sede_id") else None,
            area=qp.get("area"),
            fecha_desde=f_desde,
            fecha_hasta=f_hasta,
            solo_extras=qp.get("solo_extras", "false").lower() == "true",
            page=int(qp.get("page", 1)),
            page_size=int(qp.get("page_size", 20))
        )

        use_case = ListarAsistenciasUseCase(
            DjangoAsistenciaRepository(), 
            DjangoEmpleadoRepository(),
            DjangoSedeRepository()
        )
        outputs = use_case.execute(input_dto)
        return Response([RegistroAsistenciaOutputSerializer(o).data for o in outputs])
        
class AprobarHorasExtrasView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, registro_id):
        from modules.asistencia.application.use_cases.aprobar_horas_extras import AprobarHorasExtrasUseCase, AprobarHorasExtrasInputDTO
        try:
            dto = AprobarHorasExtrasInputDTO(
                registro_id=registro_id,
                evaluador_id=request.user.id,
                minutos_aprobados=request.data.get('minutos_aprobados', 0),
                comentario=request.data.get('comentario'),
                aprobar=request.data.get('aprobar', True)
            )
            use_case = AprobarHorasExtrasUseCase(DjangoAsistenciaRepository())
            use_case.execute(dto)
            return Response({'message': 'Horas extras evaluadas correctamente'})
        except Exception as e:
            return Response({'error': str(e)}, status=400)
