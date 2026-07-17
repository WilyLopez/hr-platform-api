from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from modules.horario.infrastructure.repositories.horario_repository_impl import (
    DjangoHorarioRepository, 
    DjangoAsignacionHorarioRepository
)
from modules.empleado.infrastructure.repositories.empleado_repository_impl import DjangoEmpleadoRepository
from modules.horario.application.dtos.asignacion_dto import AsignarHorarioInputDTO
from modules.horario.application.use_cases.asignar_horario import AsignarHorarioUseCase
from modules.horario.interfaces.serializers.asignacion_serializer import (
    AsignarHorarioSerializer, 
    AsignacionOutputSerializer
)


class AsignarHorarioView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AsignarHorarioSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        d = serializer.validated_data
        
        input_dto = AsignarHorarioInputDTO(
            empresa_id=request.empresa_id,
            empleado_id=d["empleado_id"],
            horario_id=d["horario_id"],
            fecha_desde=d["fecha_desde"],
            fecha_hasta=d.get("fecha_hasta"),
            creado_por_id=request.usuario_id
        )
        
        use_case = AsignarHorarioUseCase(
            DjangoAsignacionHorarioRepository(),
            DjangoHorarioRepository(),
            DjangoEmpleadoRepository()
        )
        output = use_case.execute(input_dto)
        
        return Response(AsignacionOutputSerializer(output).data, status=status.HTTP_201_CREATED)

class AsignacionEmpleadoListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, empleado_id):
        repo = DjangoAsignacionHorarioRepository()
        # TODO: Add security check to ensure the employee belongs to the current user's company
        
        asignaciones = repo.get_asignaciones_by_empleado(empleado_id)
        
        # Build outputs
        outputs = []
        for asig in asignaciones:
            # We fetch the schedule name as we mapped it in output dto
            h_repo = DjangoHorarioRepository()
            h = h_repo.get_horario_by_id(asig.horario_id)
            outputs.append({
                "id": asig.id,
                "empleado_id": asig.empleado_id,
                "horario_id": asig.horario_id,
                "horario_nombre": h.nombre if h else "Desconocido",
                "fecha_desde": asig.fecha_desde,
                "fecha_hasta": asig.fecha_hasta,
                "fecha_creacion": asig.fecha_creacion,
            })
            
        return Response(AsignacionOutputSerializer(outputs, many=True).data)
