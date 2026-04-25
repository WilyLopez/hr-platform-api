from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from modules.solicitud.application.dtos.solicitud_dto import (
    CrearSolicitudInputDTO, EvaluarSolicitudInputDTO, ListarSolicitudesInputDTO
)
from modules.solicitud.interfaces.serializers.solicitud_serializer import (
    CrearSolicitudSerializer, EvaluarSolicitudSerializer, SolicitudOutputSerializer
)
from modules.solicitud.infrastructure.repositories.solicitud_repository_impl import DjangoSolicitudRepository
from modules.solicitud.infrastructure.repositories.tipo_permiso_repository_impl import DjangoTipoPermisoRepository
from modules.empleado.infrastructure.repositories.empleado_repository_impl import DjangoEmpleadoRepository
from modules.solicitud.application.use_cases.crear_solicitud import CrearSolicitudUseCase
from modules.solicitud.application.use_cases.aprobar_solicitud import AprobarSolicitudUseCase
from modules.solicitud.application.use_cases.rechazar_solicitud import RechazarSolicitudUseCase
from modules.solicitud.application.use_cases.cancelar_solicitud import CancelarSolicitudUseCase
from modules.solicitud.application.use_cases.listar_solicitudes import ListarSolicitudesUseCase
from modules.auditoria.infrastructure.repositories.auditoria_repository_impl import DjangoAuditoriaRepository
from modules.auditoria.application.use_cases.registrar_evento import RegistrarEventoUseCase
from modules.notificacion.infrastructure.services.email_service import EmailService


def _auditoria():
    return RegistrarEventoUseCase(DjangoAuditoriaRepository())


class _NotifAdapter:
    def __init__(self):
        self._svc = EmailService()

    def notificar_nueva_solicitud(self, empresa_id, empleado_nombre, tipo_permiso, fecha_inicio, fecha_fin):
        pass

    def notificar_resultado_solicitud(self, empresa_id, empleado_id, tipo_permiso, resultado, comentario):
        pass


class SolicitudListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qp = request.query_params
        from datetime import date
        input_dto = ListarSolicitudesInputDTO(
            empresa_id=request.empresa_id,
            empleado_id=int(qp["empleado_id"]) if qp.get("empleado_id") else None,
            estado=qp.get("estado"),
            tipo_permiso_id=int(qp["tipo_permiso_id"]) if qp.get("tipo_permiso_id") else None,
            fecha_desde=date.fromisoformat(qp["fecha_desde"]) if qp.get("fecha_desde") else None,
            fecha_hasta=date.fromisoformat(qp["fecha_hasta"]) if qp.get("fecha_hasta") else None,
            page=int(qp.get("page", 1)),
        )
        outputs = ListarSolicitudesUseCase(
            DjangoSolicitudRepository(), DjangoEmpleadoRepository()
        ).execute(input_dto)
        return Response(SolicitudOutputSerializer(outputs, many=True).data)

    def post(self, request):
        serializer = CrearSolicitudSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        d = serializer.validated_data
        use_case = CrearSolicitudUseCase(
            solicitud_repository=DjangoSolicitudRepository(),
            tipo_permiso_repository=DjangoTipoPermisoRepository(),
            empleado_repository=DjangoEmpleadoRepository(),
            auditoria_use_case=_auditoria(),
            notificacion_use_case=_NotifAdapter(),
        )
        output = use_case.execute(CrearSolicitudInputDTO(
            empleado_id=request.usuario_id,
            empresa_id=request.empresa_id,
            **d,
        ))
        return Response(SolicitudOutputSerializer(output).data, status=status.HTTP_201_CREATED)


class SolicitudAprobarView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, solicitud_id):
        serializer = EvaluarSolicitudSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        use_case = AprobarSolicitudUseCase(
            DjangoSolicitudRepository(), DjangoEmpleadoRepository(),
            _auditoria(), _NotifAdapter(),
        )
        output = use_case.execute(EvaluarSolicitudInputDTO(
            solicitud_id=solicitud_id,
            empresa_id=request.empresa_id,
            evaluado_por_id=request.usuario_id,
            comentario=serializer.validated_data.get("comentario"),
        ))
        return Response(SolicitudOutputSerializer(output).data)


class SolicitudRechazarView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, solicitud_id):
        serializer = EvaluarSolicitudSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        use_case = RechazarSolicitudUseCase(
            DjangoSolicitudRepository(), DjangoEmpleadoRepository(),
            _auditoria(), _NotifAdapter(),
        )
        output = use_case.execute(EvaluarSolicitudInputDTO(
            solicitud_id=solicitud_id,
            empresa_id=request.empresa_id,
            evaluado_por_id=request.usuario_id,
            comentario=serializer.validated_data.get("comentario"),
        ))
        return Response(SolicitudOutputSerializer(output).data)


class SolicitudCancelarView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, solicitud_id):
        CancelarSolicitudUseCase(DjangoSolicitudRepository()).execute({
            "solicitud_id": solicitud_id,
            "empresa_id": request.empresa_id,
            "empleado_id": request.usuario_id,
        })
        return Response({"status": "ok"})