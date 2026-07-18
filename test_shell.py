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
        "empresa_id": 5,
        "suspendido_por_id": 1,
        "motivo_categoria": "OTRO",
        "comentario": "test local from shell",
        "propietario_email": "test@test.com",
        "ip_address": "127.0.0.1",
    })
    print("EXITO SUSPENDIENDO EMPRESA 5")
except Exception as e:
    import traceback
    traceback.print_exc()
