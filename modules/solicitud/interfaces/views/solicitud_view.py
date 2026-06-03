from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from modules.solicitud.application.dtos.solicitud_dto import (
    CrearSolicitudInputDTO, EvaluarSolicitudInputDTO, ListarSolicitudesInputDTO,SolicitudOutputDTO
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

class SolicitudDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, solicitud_id):
        # 1. Obtenemos la solicitud cruda de la base de datos
        sol_repo = DjangoSolicitudRepository()
        s = sol_repo.get_by_id(solicitud_id)
        
        if not s:
            return Response({"error": "Solicitud no encontrada"}, status=status.HTTP_404_NOT_FOUND)

        # 2. Obtenemos el empleado para sacar su nombre
        emp_repo = DjangoEmpleadoRepository()
        emp = emp_repo.get_by_id(s.empleado_id)
        
        if emp:
            if callable(getattr(emp, 'nombre_completo', None)):
                empleado_nombre = emp.nombre_completo()
            else:
                empleado_nombre = getattr(emp, 'nombre_completo', f"Empleado {s.empleado_id}")
        else:
            empleado_nombre = "Empleado Desconocido"

        # 3. Calculamos los días
        if callable(getattr(s, 'dias_solicitados', None)):
            dias = s.dias_solicitados()
        else:
            dias = getattr(s, 'dias_solicitados', 0)
            
        if dias == 0 and hasattr(s, 'fecha_fin') and hasattr(s, 'fecha_inicio'):
            delta = s.fecha_fin - s.fecha_inicio
            dias = delta.days + 1

        # 4. Construimos el DTO y devolvemos la respuesta
        dto = SolicitudOutputDTO(
            id=s.id,
            empresa_id=s.empresa_id,
            empleado_id=s.empleado_id,
            empleado_nombre=empleado_nombre,
            tipo_permiso_id=s.tipo_permiso_id,
            tipo_permiso_nombre=getattr(s, 'tipo_permiso_nombre', 'Permiso Estándar'),
            fecha_inicio=s.fecha_inicio,
            fecha_fin=s.fecha_fin,
            dias_solicitados=dias,
            motivo=s.motivo,
            estado=s.estado,
            adjunto_url=s.adjunto_url,
            comentario_evaluador=s.comentario_evaluador,
            evaluado_por_id=s.evaluado_por_id,
            fecha_evaluacion=s.fecha_evaluacion,
            fecha_creacion=s.fecha_creacion,
        )
        
        return Response(SolicitudOutputSerializer(dto).data)    
    