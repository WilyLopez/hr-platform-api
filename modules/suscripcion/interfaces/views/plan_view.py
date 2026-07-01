from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from modules.suscripcion.interfaces.serializers.plan_serializer import PlanOutputSerializer, CrearPlanSerializer, ActualizarPlanSerializer
from modules.suscripcion.infrastructure.repositories.plan_repository_impl import DjangoPlanRepository
from modules.suscripcion.infrastructure.repositories.suscripcion_repository_impl import DjangoSuscripcionRepository
from modules.suscripcion.application.dtos.plan_dto import PlanOutputDTO, CrearPlanInputDTO, ActualizarPlanInputDTO
from modules.suscripcion.application.use_cases.crear_plan import CrearPlanUseCase
from modules.suscripcion.application.use_cases.actualizar_plan import ActualizarPlanUseCase


class PlanListView(APIView):
    # GET is public (for registration page pricing display)
    # POST requires SUPERADMIN
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get(self, request):
        planes = DjangoPlanRepository().get_all_activos()
        outputs = []
        for p in planes:
            dto = PlanOutputDTO(
                id=p.id, nombre=p.nombre, precio_mensual=p.precio_mensual,
                limite_usuarios=p.limite_usuarios, almacenamiento_gb=p.almacenamiento_gb,
                color=p.color, descripcion_corta=p.descripcion_corta, orden=p.orden,
                es_activo=p.es_activo,
            )
            dto.empresas_count = DjangoSuscripcionRepository().count_by_plan(p.id)
            outputs.append(dto)
        return Response(PlanOutputSerializer(outputs, many=True).data)

    def post(self, request):
        if getattr(request.user, 'rol', None) != "SUPERADMIN":
            return Response({"error": "Solo el superadmin puede crear planes"}, status=403)
        
        serializer = CrearPlanSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        d = serializer.validated_data
        
        use_case = CrearPlanUseCase(DjangoPlanRepository())
        output = use_case.execute(CrearPlanInputDTO(**d))
        return Response(PlanOutputSerializer(output).data, status=201)


class PlanDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, plan_id):
        if getattr(request.user, 'rol', None) != "SUPERADMIN":
            return Response({"error": "Solo el superadmin puede editar planes"}, status=403)

        serializer = ActualizarPlanSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        d = serializer.validated_data

        use_case = ActualizarPlanUseCase(DjangoPlanRepository(), DjangoSuscripcionRepository())
        output = use_case.execute(ActualizarPlanInputDTO(plan_id=plan_id, **d))
        return Response(PlanOutputSerializer(output).data)