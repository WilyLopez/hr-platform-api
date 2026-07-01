from modules.empleado.application.use_cases.registrar_empleado import RegistrarEmpleadoUseCase
from modules.empleado.application.dtos.empleado_dto import RegistrarEmpleadoInputDTO
from modules.empleado.infrastructure.repositories.empleado_repository_impl import DjangoEmpleadoRepository
from modules.usuario.infrastructure.repositories.usuario_repository_impl import DjangoUsuarioRepository
from modules.usuario.infrastructure.repositories.rol_repository_impl import DjangoRolRepository
from modules.usuario.infrastructure.services.jwt_service import PasswordService
from modules.empleado.interfaces.views.empleado_view import _auditoria
class _SuscAdapter:
    def verificar_limites(self, eid): pass
class _UsuAdapter:
    def crear_empleado(self, empresa_id, correo, codigo_unico):
        from modules.usuario.application.use_cases.crear_usuario import CrearUsuarioUseCase, CrearUsuarioInputDTO
        import secrets, string
        contrasena = 'admin123456'
        uc = CrearUsuarioUseCase(DjangoUsuarioRepository(), DjangoRolRepository(), PasswordService(), _auditoria())
        return uc.execute(CrearUsuarioInputDTO(empresa_id=empresa_id, rol_nombre='EMPLEADO', correo=correo, contrasena=contrasena))
class _NotifAdapter:
    def notificar_bienvenida_empleado(self, correo, codigo_unico): pass
use_case = RegistrarEmpleadoUseCase(DjangoEmpleadoRepository(), _SuscAdapter(), _UsuAdapter(), _auditoria(), _NotifAdapter())
use_case.execute(RegistrarEmpleadoInputDTO(empresa_id=4, sede_id=1, nombres='Juan', apellidos='Perez', tipo_documento='DNI', numero_documento='92345678', correo='juan3@empresa.com', telefono='123456789', cargo='Desarrollador', fecha_ingreso='2026-06-29', area='IT'))
