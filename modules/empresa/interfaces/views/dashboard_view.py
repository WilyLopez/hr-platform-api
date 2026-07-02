from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from modules.empresa.infrastructure.models.empresa_model import EmpresaModel
from modules.usuario.infrastructure.models.usuario_model import UsuarioModel
from modules.suscripcion.infrastructure.models.suscripcion_model import SuscripcionModel
from shared.constants import RolesUsuario, EstadosSuscripcion, EstadosEmpresa
from django.db.models import Sum


class SuperadminDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.rol != RolesUsuario.SUPERADMIN:
            return Response({"error": "No autorizado"}, status=403)

        total_empresas = EmpresaModel.objects.exclude(estado=EstadosEmpresa.ELIMINADA).count()
        total_usuarios = UsuarioModel.objects.count()
        
        pruebas_activas = SuscripcionModel.objects.filter(estado=EstadosSuscripcion.TRIAL).count()
        
        
        # Calcular MRR estimado (suma de precios de planes de suscripciones activas)
        suscripciones_activas = SuscripcionModel.objects.filter(estado=EstadosSuscripcion.ACTIVA).select_related('plan')
        mrr = sum(s.plan.precio_mensual for s in suscripciones_activas if s.plan)

        return Response({
            "total_empresas": total_empresas,
            "total_usuarios": total_usuarios,
            "pruebas_activas": pruebas_activas,
            "mrr_estimado": float(mrr),
        })
