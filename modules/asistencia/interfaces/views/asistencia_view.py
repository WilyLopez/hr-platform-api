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
)
from modules.asistencia.infrastructure.repositories.asistencia_repository_impl import DjangoAsistenciaRepository
from modules.asistencia.infrastructure.repositories.qr_repository_impl import DjangoQrRepository
from modules.empleado.infrastructure.repositories.empleado_repository_impl import DjangoEmpleadoRepository
from modules.empresa.infrastructure.repositories.sede_repository_impl import DjangoSedeRepository
from modules.solicitud.infrastructure.repositories.solicitud_repository_impl import DjangoSolicitudRepository
from modules.asistencia.infrastructure.services.geolocalizacion_service import GeolocalizacionService
from modules.asistencia.application.use_cases.validar_geolocalizacion import ValidarGeolocalizacionUseCase
from modules.asistencia.application.use_cases.registrar_marcaje import RegistrarMarcajeUseCase
from modules.asistencia.application.use_cases.registrar_manual import RegistrarManualUseCase
from modules.asistencia.application.use_cases.generar_reporte import GenerarReporteAsistenciaUseCase
from modules.auditoria.infrastructure.repositories.auditoria_repository_impl import DjangoAuditoriaRepository
from modules.auditoria.application.use_cases.registrar_evento import RegistrarEventoUseCase
from modules.asistencia.application.use_cases.listar_asistencias import ListarAsistenciasUseCase

def _auditoria():
    return RegistrarEventoUseCase(DjangoAuditoriaRepository())


class MarcajeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = RegistrarMarcajeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        d = serializer.validated_data
        use_case = RegistrarMarcajeUseCase(
            asistencia_repository=DjangoAsistenciaRepository(),
            qr_repository=DjangoQrRepository(),
            empleado_repository=DjangoEmpleadoRepository(),
            sede_repository=DjangoSedeRepository(),
            solicitud_repository=DjangoSolicitudRepository(),
            validar_geo_use_case=ValidarGeolocalizacionUseCase(GeolocalizacionService()),
            auditoria_use_case=_auditoria(),
        )
        output = use_case.execute(RegistrarMarcajeInputDTO(
            empleado_id=request.usuario_id,
            empresa_id=request.empresa_id,
            **d,
        ))
        return Response(RegistroAsistenciaOutputSerializer(output).data, status=status.HTTP_201_CREATED)


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
            empresa_id=request.empresa_id,
            admin_id=request.usuario_id,
            **d,
        ))
        return Response(RegistroAsistenciaOutputSerializer(output).data, status=status.HTTP_201_CREATED)


class ReporteAsistenciaView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from datetime import date
        qp = request.query_params
        input_dto = ListarAsistenciaInputDTO(
            empresa_id=request.empresa_id,
            empleado_id=int(qp["empleado_id"]) if qp.get("empleado_id") else None,
            sede_id=int(qp["sede_id"]) if qp.get("sede_id") else None,
            area=qp.get("area"),
            fecha_desde=date.fromisoformat(qp["fecha_desde"]) if qp.get("fecha_desde") else None,
            fecha_hasta=date.fromisoformat(qp["fecha_hasta"]) if qp.get("fecha_hasta") else None,
        )
        use_case = GenerarReporteAsistenciaUseCase(
            DjangoAsistenciaRepository(), DjangoEmpleadoRepository()
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
            empresa_id=request.empresa_id,
            empleado_id=int(qp["empleado_id"]) if qp.get("empleado_id") else None,
            sede_id=int(qp["sede_id"]) if qp.get("sede_id") else None,
            area=qp.get("area"),
            fecha_desde=f_desde,
            fecha_hasta=f_hasta,
            page=int(qp.get("page", 1)),
            page_size=int(qp.get("page_size", 20))
        )

        use_case = ListarAsistenciasUseCase(
            DjangoAsistenciaRepository(), 
            DjangoEmpleadoRepository()
        )
        outputs = use_case.execute(input_dto)
        
        return Response(RegistroAsistenciaOutputSerializer(outputs, many=True).data)    