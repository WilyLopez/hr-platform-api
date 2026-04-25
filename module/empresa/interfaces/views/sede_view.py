from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from modules.empresa.application.dtos.sede_dto import CrearSedeInputDTO, ActualizarSedeInputDTO
from modules.empresa.interfaces.serializers.sede_serializer import (
    CrearSedeSerializer,
    ActualizarSedeSerializer,
    SedeOutputSerializer,
)
from modules.empresa.infrastructure.repositories.sede_repository_impl import DjangoSedeRepository
from modules.empresa.infrastructure.repositories.empresa_repository_impl import DjangoEmpresaRepository
from modules.empresa.application.use_cases.crear_sede import CrearSedeUseCase
from modules.empresa.application.use_cases.configurar_geovalla import ConfigurarGeovallaUseCase


class SedeListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, empresa_id):
        sedes = DjangoSedeRepository().get_by_empresa(empresa_id)
        from modules.empresa.application.dtos.sede_dto import SedeOutputDTO
        outputs = [
            SedeOutputDTO(
                id=s.id, empresa_id=s.empresa_id, nombre=s.nombre,
                direccion=s.direccion, latitud=s.coordenadas.latitud,
                longitud=s.coordenadas.longitud, radio_metros=s.radio_metros.value,
                es_activa=s.es_activa,
            )
            for s in sedes
        ]
        return Response(SedeOutputSerializer(outputs, many=True).data)

    def post(self, request, empresa_id):
        serializer = CrearSedeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        d = serializer.validated_data
        use_case = CrearSedeUseCase(DjangoSedeRepository(), DjangoEmpresaRepository())
        output = use_case.execute(CrearSedeInputDTO(empresa_id=empresa_id, **d))
        return Response(SedeOutputSerializer(output).data, status=status.HTTP_201_CREATED)


class SedeDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, empresa_id, sede_id):
        serializer = ActualizarSedeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        d = serializer.validated_data
        use_case = ConfigurarGeovallaUseCase(DjangoSedeRepository())
        output = use_case.execute(ActualizarSedeInputDTO(sede_id=sede_id, empresa_id=empresa_id, **d))
        return Response(SedeOutputSerializer(output).data)