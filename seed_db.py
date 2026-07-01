import os
import sys

# Add the current directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure Django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")

import django
django.setup()

try:
    from modules.usuario.infrastructure.models.rol_model import RolModel
    from modules.suscripcion.infrastructure.models.plan_model import PlanModel

    # Seed base Roles
    roles = ["PROPIETARIO", "ADMIN", "EMPLEADO", "SUPERADMIN"]
    for r in roles:
        rol, created = RolModel.objects.get_or_create(
            nombre=r,
            empresa_id=None,
            defaults={
                "permisos": ["ALL"],
                "es_sistema": True
            }
        )
        print(f"Role {r} {'created' if created else 'already exists'}.")

    # Seed Plans
    plan_basico, created = PlanModel.objects.get_or_create(
        id=1,
        defaults={
            "nombre": "BASICO",
            "precio_mensual": 0.00,
            "limite_usuarios": 10,
            "almacenamiento_gb": 5,
            "es_activo": True
        }
    )
    if created:
        print("Plan Básico created.")
    else:
        print("Plan Básico already exists.")

    plan_pro, created = PlanModel.objects.get_or_create(
        id=2,
        defaults={
            "nombre": "PRO",
            "precio_mensual": 99.00,
            "limite_usuarios": 100,
            "almacenamiento_gb": 50,
            "es_activo": True
        }
    )
    if created:
        print("Plan Pro created.")
    else:
        print("Plan Pro already exists.")

    print("Success: Database seeded successfully.")

except Exception as e:
    print(f"Error seeding data: {e}")
