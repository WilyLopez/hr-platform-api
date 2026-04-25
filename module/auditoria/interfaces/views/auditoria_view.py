from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponse

from modules.auditoria.application.dtos.auditoria_dto import ConsultarAuditoriaInputDTO, ExportarAuditoriaInputDTO
from modules.auditoria.interfaces.serializers.auditoria_serializer import (
    ConsultarAuditoriaSerializer,
    ExportarAuditoriaSerializer,
    RegistroAuditoriaOutputSerializer,
)
from modules.auditoria.infrastructure.repositories.auditoria_repository_impl import DjangoAuditoriaRepository
from modules.auditoria.infrastructure.services.exportacion_service import ExportacionService
from modules.auditoria.application.use_cases.consultar_auditoria import ConsultarAuditoriaUseCase
from modules.auditoria.application.use_cases.exportar_auditoria import ExportarAuditoriaUseCase


class AuditoriaListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = ConsultarAuditoriaSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        d = serializer.validated_data
        use_case = ConsultarAuditoriaUseCase(DjangoAuditoriaRepository())
        outputs = use_case.execute(ConsultarAuditoriaInputDTO(
            empresa_id=request.empresa_id,
            usuario_id=d.get("usuario_id"),
            rol=d.get("rol"),
            tipo_evento=d.get("tipo_evento"),
            fecha_desde=d.get("fecha_desde"),
            fecha_hasta=d.get("fecha_hasta"),
            page=int(request.query_params.get("page", 1)),
        ))
        return Response(RegistroAuditoriaOutputSerializer(outputs, many=True).data)


class AuditoriaExportarView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ExportarAuditoriaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        d = serializer.validated_data
        use_case = ExportarAuditoriaUseCase(DjangoAuditoriaRepository(), ExportacionService())
        contenido = use_case.execute(ExportarAuditoriaInputDTO(
            empresa_id=request.empresa_id,
            fecha_desde=d["fecha_desde"],
            fecha_hasta=d["fecha_hasta"],
            formato=d["formato"],
        ))
        fmt = d["formato"].upper()
        content_type = "application/pdf" if fmt == "PDF" else "text/csv"
        ext = "pdf" if fmt == "PDF" else "csv"
        response = HttpResponse(contenido, content_type=content_type)
        response["Content-Disposition"] = f'attachment; filename="auditoria.{ext}"'
        return response