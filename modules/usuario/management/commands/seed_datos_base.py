from django.core.management.base import BaseCommand

from modules.usuario.infrastructure.models.rol_model import RolModel
from modules.suscripcion.infrastructure.models.plan_model import PlanModel
from shared.constants import RolesUsuario, PlanesNombre


class Command(BaseCommand):
    """Siembra los roles globales del sistema y los planes de suscripcion.

    Sin estos datos base, nada funciona: el registro publico de una empresa
    (POST /api/v1/empresas/registro/) busca el rol "PROPIETARIO" y un
    plan_id existentes, y falla si la base esta vacia. Es idempotente
    (usa get_or_create), asi que es seguro correrlo en cada deploy.
    """

    help = "Siembra los roles globales del sistema y los planes de suscripcion base."

    def handle(self, *args, **options):
        roles_creados = 0
        for nombre, _ in RolesUsuario.CHOICES:
            _, creado = RolModel.objects.get_or_create(
                empresa_id=None,
                nombre=nombre,
                defaults={"permisos": [], "es_sistema": True},
            )
            roles_creados += int(creado)

        planes = [
            {"nombre": PlanesNombre.BASICO, "precio_mensual": 49.90, "limite_usuarios": 20, "almacenamiento_gb": 5},
            {"nombre": PlanesNombre.PRO, "precio_mensual": 99.90, "limite_usuarios": 100, "almacenamiento_gb": 20},
        ]
        planes_creados = 0
        for plan in planes:
            nombre = plan.pop("nombre")
            _, creado = PlanModel.objects.get_or_create(
                nombre=nombre,
                defaults={**plan, "es_activo": True},
            )
            planes_creados += int(creado)

        self.stdout.write(self.style.SUCCESS(
            f"Roles nuevos: {roles_creados}/{len(RolesUsuario.CHOICES)}. "
            f"Planes nuevos: {planes_creados}/{len(planes)}."
        ))
