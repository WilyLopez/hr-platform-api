from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from modules.suscripcion.interfaces.serializers.suscripcion_serializer import (
    CambiarPlanSerializer,
    SuscripcionOutputSerializer,
)
from modules.suscripcion.application.dtos.suscripcion_dto import CambiarPlanInputDTO
from modules.suscripcion.infrastructure.repositories.suscripcion_repository_impl import DjangoSuscripcionRepository
from modules.suscripcion.infrastructure.repositories.plan_repository_impl import DjangoPlanRepository
from modules.suscripcion.application.use_cases.obtener_estado import ObtenerEstadoSuscripcionUseCase
from modules.suscripcion.application.use_cases.cambiar_plan import CambiarPlanUseCase


class SuscripcionDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        output = ObtenerEstadoSuscripcionUseCase(DjangoSuscripcionRepository()).execute(
            request.empresa_id
        )
        return Response(SuscripcionOutputSerializer(output).data)


class CambiarPlanView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CambiarPlanSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        output = CambiarPlanUseCase(
            DjangoSuscripcionRepository(), DjangoPlanRepository()
        ).execute(CambiarPlanInputDTO(
            empresa_id=request.empresa_id,
            nuevo_plan_id=serializer.validated_data["nuevo_plan_id"],
        ))
        return Response(SuscripcionOutputSerializer(output).data)


class SuperadminCambiarPlanView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, empresa_id):
        if request.rol != "SUPERADMIN":
            return Response({"error": "No autorizado"}, status=403)
            
        serializer = CambiarPlanSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        output = CambiarPlanUseCase(
            DjangoSuscripcionRepository(), DjangoPlanRepository()
        ).execute(CambiarPlanInputDTO(
            empresa_id=empresa_id,
            nuevo_plan_id=serializer.validated_data["nuevo_plan_id"],
        ))

        # Registrar auditoría
        from modules.auditoria.application.use_cases.registrar_evento import RegistrarEventoUseCase
        from modules.auditoria.application.dtos.auditoria_dto import RegistrarEventoInputDTO
        from modules.auditoria.infrastructure.repositories.auditoria_repository_impl import DjangoAuditoriaRepository
        from shared.constants import TiposEvento
        RegistrarEventoUseCase(DjangoAuditoriaRepository()).execute(
            RegistrarEventoInputDTO(
                empresa_id=empresa_id,
                usuario_id=request.usuario_id,
                rol_usuario=request.rol,
                tipo_evento=TiposEvento.CAMBIO_PLAN,
                descripcion=f"El Superadmin cambió el plan de la empresa a: {output.plan_nombre}",
                ip_address=request.META.get('REMOTE_ADDR'),
                detalles={"nuevo_plan_id": output.plan_id, "nuevo_plan_nombre": output.plan_nombre},
            )
        )

        return Response(SuscripcionOutputSerializer(output).data)


class SuperadminSuscripcionesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.rol != "SUPERADMIN":
            return Response({"error": "No autorizado"}, status=403)

        from modules.suscripcion.infrastructure.models.suscripcion_model import SuscripcionModel
        from modules.empresa.infrastructure.models.empresa_model import EmpresaModel

        estado = request.query_params.get("estado")
        qs = SuscripcionModel.objects.select_related('plan').all().order_by('-fecha_creacion')
        if estado:
            qs = qs.filter(estado=estado)

        results = []
        for s in qs:
            try:
                empresa = EmpresaModel.objects.get(pk=s.empresa_id)
                empresa_nombre = empresa.razon_social
            except EmpresaModel.DoesNotExist:
                empresa_nombre = f"Empresa #{s.empresa_id}"

            results.append({
                "id": s.pk,
                "empresa_id": s.empresa_id,
                "empresa_nombre": empresa_nombre,
                "plan_id": s.plan_id,
                "plan_nombre": s.plan.nombre if s.plan else "—",
                "estado": s.estado,
                "fecha_inicio": s.fecha_inicio,
                "fecha_fin_trial": s.fecha_fin_trial,
                "fecha_proxima_facturacion": s.fecha_proxima_facturacion,
                "usuarios_activos": s.usuarios_activos,
                "limite_usuarios": s.plan.limite_usuarios if s.plan else 0,
                "fecha_creacion": s.fecha_creacion,
            })

        return Response(results)