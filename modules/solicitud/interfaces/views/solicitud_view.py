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
from modules.solicitud.application.use_cases.obtener_solicitud import ObtenerSolicitudUseCase, ObtenerSolicitudInputDTO
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
        page = int(qp.get("page", 1))
        page_size = int(qp.get("page_size", 20))
        input_dto = ListarSolicitudesInputDTO(
            empresa_id=request.user.empresa_id,
            empleado_id=int(qp["empleado_id"]) if qp.get("empleado_id") else None,
            estado=qp.get("estado"),
            tipo_permiso_id=int(qp["tipo_permiso_id"]) if qp.get("tipo_permiso_id") else None,
            fecha_desde=date.fromisoformat(qp["fecha_desde"]) if qp.get("fecha_desde") else None,
            fecha_hasta=date.fromisoformat(qp["fecha_hasta"]) if qp.get("fecha_hasta") else None,
            page=page,
            page_size=page_size,
        )
        outputs = ListarSolicitudesUseCase(
            DjangoSolicitudRepository(), DjangoEmpleadoRepository()
        ).execute(input_dto)

        # Obtener el total para construir la respuesta paginada estándar
        from modules.solicitud.infrastructure.models.solicitud_model import SolicitudModel
        qs = SolicitudModel.objects.filter(empresa_id=request.user.empresa_id)
        if input_dto.estado:
            qs = qs.filter(estado=input_dto.estado)
        if input_dto.empleado_id:
            qs = qs.filter(empleado_id=input_dto.empleado_id)
        if input_dto.tipo_permiso_id:
            qs = qs.filter(tipo_permiso_id=input_dto.tipo_permiso_id)
        if input_dto.fecha_desde:
            qs = qs.filter(fecha_inicio__gte=input_dto.fecha_desde)
        if input_dto.fecha_hasta:
            qs = qs.filter(fecha_fin__lte=input_dto.fecha_hasta)
        total = qs.count()

        base_url = request.build_absolute_uri(request.path)
        def _page_url(p):
            params = qp.copy()
            params["page"] = p
            return f"{base_url}?{'&'.join(f'{k}={v}' for k, v in params.items())}"

        has_next = (page * page_size) < total
        has_prev = page > 1

        return Response({
            "count":    total,
            "next":     _page_url(page + 1) if has_next else None,
            "previous": _page_url(page - 1) if has_prev else None,
            "results":  SolicitudOutputSerializer(outputs, many=True).data,
        })

    def post(self, request):
        serializer = CrearSolicitudSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        d = serializer.validated_data
        empleado_repo = DjangoEmpleadoRepository()
        empleado = empleado_repo.get_by_usuario_id(request.user.id)
        if not empleado:
            return Response({"error": "Empleado no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        use_case = CrearSolicitudUseCase(
            solicitud_repository=DjangoSolicitudRepository(),
            tipo_permiso_repository=DjangoTipoPermisoRepository(),
            empleado_repository=empleado_repo,
            auditoria_use_case=_auditoria(),
            notificacion_use_case=_NotifAdapter(),
        )
        output = use_case.execute(CrearSolicitudInputDTO(
            empleado_id=empleado.id,
            empresa_id=request.user.empresa_id,
            **d,
        ))
        return Response(SolicitudOutputSerializer(output).data, status=status.HTTP_201_CREATED)



class SolicitudDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, solicitud_id):
        use_case = ObtenerSolicitudUseCase(
            DjangoSolicitudRepository(), DjangoEmpleadoRepository()
        )
        input_dto = ObtenerSolicitudInputDTO(
            solicitud_id=solicitud_id,
            empresa_id=request.user.empresa_id,
        )
        output = use_case.execute(input_dto)
        return Response(SolicitudOutputSerializer(output).data)

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
            empresa_id=request.user.empresa_id,
            evaluado_por_id=request.user.id,
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
            empresa_id=request.user.empresa_id,
            evaluado_por_id=request.user.id,
            comentario=serializer.validated_data.get("comentario"),
        ))
        return Response(SolicitudOutputSerializer(output).data)


class SolicitudCancelarView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, solicitud_id):
        empleado = DjangoEmpleadoRepository().get_by_usuario_id(request.user.id)
        if not empleado:
            return Response({"error": "Empleado no encontrado"}, status=status.HTTP_404_NOT_FOUND)
            
        CancelarSolicitudUseCase(DjangoSolicitudRepository()).execute({
            "solicitud_id": solicitud_id,
            "empresa_id": request.user.empresa_id,
            "empleado_id": empleado.id,
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
    
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import uuid
import os

# Tipos de archivo permitidos para adjuntos de solicitudes
ALLOWED_EXTENSIONS = {'.pdf', '.jpg', '.jpeg', '.png'}
ALLOWED_MIME_PREFIXES = ('application/pdf', 'image/jpeg', 'image/png')
MAX_UPLOAD_SIZE_MB = 5
MAX_UPLOAD_SIZE_BYTES = MAX_UPLOAD_SIZE_MB * 1024 * 1024


class ArchivoUploadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        file = request.FILES.get('file')
        if not file:
            return Response({"error": "No se envió ningún archivo."}, status=status.HTTP_400_BAD_REQUEST)

        # ── Validación de tamaño ──────────────────────────────────────────────
        if file.size > MAX_UPLOAD_SIZE_BYTES:
            return Response(
                {"error": f"El archivo excede el tamaño máximo permitido de {MAX_UPLOAD_SIZE_MB} MB."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ── Validación de extensión ───────────────────────────────────────────
        ext = os.path.splitext(file.name)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            return Response(
                {"error": f"Tipo de archivo no permitido. Se aceptan: {', '.join(ALLOWED_EXTENSIONS)}."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ── Validación de Content-Type declarado ─────────────────────────────
        content_type = file.content_type or ''
        if not any(content_type.startswith(prefix) for prefix in ALLOWED_MIME_PREFIXES):
            return Response(
                {"error": "El tipo MIME del archivo no está permitido."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ── Guardar con nombre aleatorio para evitar colisiones ───────────────
        filename = f"{uuid.uuid4().hex}{ext}"
        fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'uploads'))
        saved_name = fs.save(filename, file)

        file_url = request.build_absolute_uri(f"{settings.MEDIA_URL}uploads/{saved_name}")
        return Response({"url": file_url}, status=status.HTTP_201_CREATED)
