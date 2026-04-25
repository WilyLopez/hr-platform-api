from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from modules.asistencia.application.dtos.qr_dto import GenerarQrInputDTO
from modules.asistencia.interfaces.serializers.qr_serializer import GenerarQrSerializer, QrOutputSerializer
from modules.asistencia.infrastructure.repositories.qr_repository_impl import DjangoQrRepository
from modules.empresa.infrastructure.repositories.sede_repository_impl import DjangoSedeRepository
from modules.asistencia.infrastructure.services.qr_generator_service import QrGeneratorService
from modules.asistencia.application.use_cases.generar_qr import GenerarQrUseCase


class GenerarQrView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, sede_id):
        serializer = GenerarQrSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        use_case = GenerarQrUseCase(
            qr_repository=DjangoQrRepository(),
            sede_repository=DjangoSedeRepository(),
            qr_generator_service=QrGeneratorService(),
        )
        output = use_case.execute(GenerarQrInputDTO(
            empresa_id=request.empresa_id,
            sede_id=sede_id,
            minutos_vigencia=serializer.validated_data.get("minutos_vigencia"),
        ))
        return Response(QrOutputSerializer(output).data, status=status.HTTP_201_CREATED)