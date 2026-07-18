import os
import sys
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from modules.empresa.infrastructure.repositories.empresa_repository_impl import DjangoEmpresaRepository
from modules.suscripcion.infrastructure.repositories.suscripcion_repository_impl import DjangoSuscripcionRepository
from modules.auditoria.infrastructure.repositories.auditoria_repository_impl import DjangoAuditoriaRepository
from modules.auditoria.application.use_cases.registrar_evento import RegistrarEventoUseCase
from modules.notificacion.infrastructure.services.email_service import EmailService
from modules.empresa.application.use_cases.suspender_empresa import SuspenderEmpresaUseCase

try:
    use_case = SuspenderEmpresaUseCase(
        DjangoEmpresaRepository(),
        DjangoSuscripcionRepository(),
        RegistrarEventoUseCase(DjangoAuditoriaRepository()),
        EmailService()
    )

    use_case.execute({
        "empresa_id": 10,
        "suspendido_por_id": 1,
        "motivo_categoria": "OTRO",
        "comentario": "test",
        "propietario_email": "test@test.com",
        "ip_address": "127.0.0.1",
    })
    print("Exito!")
except Exception as e:
    import traceback
    traceback.print_exc()

print("--- Ahora probando get_by_empresa ---")
try:
    repo = DjangoSuscripcionRepository()
    sub = repo.get_by_empresa(10)
    print(f"Sub: {sub}")
except Exception as e:
    import traceback
    traceback.print_exc()

print("--- Ahora probando cambiar plan ---")
from modules.suscripcion.application.use_cases.cambiar_plan import CambiarPlanSuperadminUseCase
from modules.suscripcion.infrastructure.repositories.plan_repository_impl import DjangoPlanRepository
try:
    use_case2 = CambiarPlanSuperadminUseCase(
        DjangoSuscripcionRepository(),
        DjangoPlanRepository(),
        RegistrarEventoUseCase(DjangoAuditoriaRepository()),
        DjangoEmpresaRepository() # Check what it expects
    )
    # just print use_case2
    print(use_case2)
except Exception as e:
    import traceback
    traceback.print_exc()
