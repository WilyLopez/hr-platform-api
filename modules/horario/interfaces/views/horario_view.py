from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from modules.horario.infrastructure.repositories.horario_repository_impl import (
    DjangoHorarioRepository, 
    DjangoTurnoRepository, 
    DjangoAsignacionHorarioRepository
)
from modules.horario.application.dtos.horario_dto import (
    CrearHorarioInputDTO, 
    ActualizarHorarioInputDTO, 
    TurnoInputDTO
)
from modules.horario.application.use_cases.crear_horario import CrearHorarioUseCase
from modules.horario.application.use_cases.actualizar_horario import ActualizarHorarioUseCase
from modules.horario.application.use_cases.listar_horarios import ListarHorariosUseCase, ListarHorariosInputDTO
from modules.horario.application.use_cases.obtener_horario import ObtenerHorarioUseCase
from modules.horario.application.use_cases.eliminar_horario import EliminarHorarioUseCase
from modules.horario.interfaces.serializers.horario_serializer import (
    CrearHorarioSerializer, 
    ActualizarHorarioSerializer, 
    HorarioOutputSerializer
)


def _repos():
    return DjangoHorarioRepository(), DjangoTurnoRepository(), DjangoAsignacionHorarioRepository()


class HorarioListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        h_repo, t_repo, a_repo = _repos()
        use_case = ListarHorariosUseCase(h_repo, t_repo, a_repo)
        
        include_inactive = request.query_params.get("include_inactive", "false").lower() == "true"
        input_dto = ListarHorariosInputDTO(
            empresa_id=request.empresa_id,
            include_inactive=include_inactive
        )
        
        output = use_case.execute(input_dto)
        return Response(HorarioOutputSerializer(output, many=True).data)

    def post(self, request):
        serializer = CrearHorarioSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        d = serializer.validated_data
        
        turnos_dto = [TurnoInputDTO(**t) for t in d.pop('turnos')]
        input_dto = CrearHorarioInputDTO(
            empresa_id=request.empresa_id,
            turnos=turnos_dto,
            **d
        )
        
        h_repo, t_repo, _ = _repos()
        use_case = CrearHorarioUseCase(h_repo, t_repo)
        output = use_case.execute(input_dto)
        
        return Response(HorarioOutputSerializer(output).data, status=status.HTTP_201_CREATED)


class HorarioDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, horario_id):
        h_repo, t_repo, a_repo = _repos()
        use_case = ObtenerHorarioUseCase(h_repo, t_repo, a_repo)
        output = use_case.execute(horario_id)
        
        # Validar que pertenece a la empresa actual
        if output.id:  # Ya está creado
            horario = h_repo.get_horario_by_id(horario_id)
            if horario and horario.empresa_id != request.empresa_id:
                return Response({"message": "No tiene permiso"}, status=status.HTTP_403_FORBIDDEN)
                
        return Response(HorarioOutputSerializer(output).data)

    def put(self, request, horario_id):
        serializer = ActualizarHorarioSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        d = serializer.validated_data
        
        turnos_dto = [TurnoInputDTO(**t) for t in d.pop('turnos')]
        input_dto = ActualizarHorarioInputDTO(
            horario_id=horario_id,
            empresa_id=request.empresa_id,
            turnos=turnos_dto,
            **d
        )
        
        h_repo, t_repo, a_repo = _repos()
        use_case = ActualizarHorarioUseCase(h_repo, t_repo, a_repo)
        output = use_case.execute(input_dto)
        
        return Response(HorarioOutputSerializer(output).data)

    def delete(self, request, horario_id):
        h_repo, _, a_repo = _repos()
        use_case = EliminarHorarioUseCase(h_repo, a_repo)
        use_case.execute(horario_id)
        
        return Response(status=status.HTTP_204_NO_CONTENT)
