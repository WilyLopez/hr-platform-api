import random
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from modules.empresa.infrastructure.models.empresa_model import EmpresaModel
from modules.empresa.infrastructure.models.sede_model import SedeModel
from modules.suscripcion.infrastructure.models.plan_model import PlanModel
from modules.suscripcion.infrastructure.models.suscripcion_model import SuscripcionModel
from modules.usuario.infrastructure.models.usuario_model import UsuarioModel
from modules.usuario.infrastructure.models.rol_model import RolModel
from modules.usuario.infrastructure.services.jwt_service import PasswordService
from modules.empleado.infrastructure.models.empleado_model import EmpleadoModel
from shared.constants import (
    RolesUsuario,
    EstadosUsuario,
    EstadosSeguridadUsuario,
    EstadosEmpresa,
    EstadosSuscripcion,
    EstadosEmpleado,
    TiposDocumento,
    PlanesNombre,
)

DEMO_PASSWORD = "Demo1234!"

NOMBRES_M = [
    "Carlos", "Jose", "Luis", "Miguel", "Jorge", "Juan", "Diego", "Fernando",
    "Ricardo", "Manuel", "Alberto", "Andres", "Cesar", "Eduardo", "Gonzalo",
    "Hugo", "Ivan", "Javier", "Leonardo", "Mario", "Oscar", "Pedro", "Raul",
    "Sergio", "Victor", "Walter", "Alexander", "Bruno", "Daniel", "Enrique",
    "Felipe", "Gabriel", "Hernan", "Ignacio", "Julio", "Kevin", "Marco",
    "Nestor", "Omar", "Pablo",
]
NOMBRES_F = [
    "Maria", "Rosa", "Ana", "Carmen", "Luz", "Patricia", "Sandra", "Karen",
    "Diana", "Gabriela", "Silvia", "Teresa", "Veronica", "Ximena", "Yolanda",
    "Alejandra", "Beatriz", "Claudia", "Daniela", "Elena", "Fiorella",
    "Gladys", "Ines", "Julia", "Katherine", "Lorena", "Melissa", "Norma",
    "Paola", "Rocio", "Sofia", "Tatiana", "Ursula", "Valeria", "Wendy",
    "Yesenia", "Zoila", "Angela", "Brenda", "Carla",
]
APELLIDOS = [
    "Garcia", "Rodriguez", "Gonzalez", "Fernandez", "Lopez", "Martinez",
    "Sanchez", "Perez", "Gomez", "Diaz", "Vargas", "Castillo", "Rojas",
    "Torres", "Flores", "Reyes", "Chavez", "Ramos", "Mendoza", "Ruiz",
    "Aguirre", "Salazar", "Quispe", "Mamani", "Huaman", "Paredes",
    "Espinoza", "Carrasco", "Ibarra", "Cordova", "Valdivia", "Zapata",
    "Ponce", "Guerrero", "Rivera", "Silva", "Vega", "Campos", "Bravo",
    "Medina",
]

AREAS_CARGOS = {
    "Recursos Humanos": ["Asistente", "Analista", "Coordinador", "Especialista"],
    "Contabilidad": ["Asistente Contable", "Analista Contable", "Contador Junior"],
    "Ventas": ["Ejecutivo Comercial", "Asesor de Ventas", "Coordinador Comercial"],
    "Operaciones": ["Supervisor de Operaciones", "Analista de Operaciones", "Asistente Operativo"],
    "Logistica": ["Coordinador de Almacen", "Analista Logistico", "Asistente de Distribucion"],
    "Sistemas": ["Analista de Sistemas", "Soporte Tecnico", "Desarrollador"],
    "Marketing": ["Especialista de Marketing", "Community Manager", "Analista de Marketing"],
    "Atencion al Cliente": ["Representante de Atencion al Cliente", "Supervisor de Call Center"],
    "Produccion": ["Operario de Produccion", "Supervisor de Planta", "Tecnico de Calidad"],
    "Legal": ["Asistente Legal", "Analista de Cumplimiento"],
}

EMPRESAS_DEMO = [
    {
        "slug": "AND",
        "ruc": "20601234567",
        "razon_social": "Andina Textiles S.A.C.",
        "nombre_comercial": "Andina Textiles",
        "dominio": "andinatextiles.pe",
        "telefono": "014567890",
        "direccion": "Av. Argentina 1234, Callao",
        "sede": {"nombre": "Sede Principal Callao", "lat": -12.0546, "lon": -77.1181},
        "plan": PlanesNombre.PRO,
        "n_empleados": 110,
    },
    {
        "slug": "CLA",
        "ruc": "20602345678",
        "razon_social": "Constructora Los Andes S.A.",
        "nombre_comercial": "Constructora Los Andes",
        "dominio": "losandesconstructora.pe",
        "telefono": "016789012",
        "direccion": "Av. Javier Prado Este 4200, Surco",
        "sede": {"nombre": "Sede Central Surco", "lat": -12.1024, "lon": -76.9880},
        "plan": PlanesNombre.PRO,
        "n_empleados": 130,
    },
    {
        "slug": "GAP",
        "ruc": "20603456789",
        "razon_social": "Grupo Alimentario del Pacifico S.A.C.",
        "nombre_comercial": "Alimentos del Pacifico",
        "dominio": "alimentosdelpacifico.pe",
        "telefono": "013456789",
        "direccion": "Av. Nestor Gambetta 3500, Ventanilla",
        "sede": {"nombre": "Planta Ventanilla", "lat": -11.8825, "lon": -77.1256},
        "plan": PlanesNombre.BASICO,
        "n_empleados": 105,
    },
]


class Command(BaseCommand):
    """Siembra datos de demostracion: un superadmin, 3 empresas cada una con
    su sede, suscripcion, 1 propietario, 2 administradores, un empleado con
    acceso al app movil, y minimo 100 empleados con nombres realistas.

    Idempotente a nivel de empresa: si una empresa con el RUC objetivo ya
    existe, se omite por completo (no duplica datos en corridas repetidas).
    Requiere que 'seed_datos_base' ya haya corrido (roles y planes).
    """

    help = "Siembra empresas, usuarios y empleados de demostracion con nombres realistas."

    def handle(self, *args, **options):
        random.seed(42)
        password_service = PasswordService()

        self._crear_superadmin(password_service)

        for empresa_cfg in EMPRESAS_DEMO:
            if EmpresaModel.objects.filter(ruc=empresa_cfg["ruc"]).exists():
                self.stdout.write(f"Empresa {empresa_cfg['razon_social']} ya existe, se omite.")
                continue
            with transaction.atomic():
                self._crear_empresa_completa(empresa_cfg, password_service)

        self.stdout.write(self.style.SUCCESS("Seed de datos de demostracion completado."))

    def _crear_superadmin(self, password_service):
        rol = RolModel.objects.get(nombre=RolesUsuario.SUPERADMIN, empresa_id=None)
        _, creado = UsuarioModel.objects.get_or_create(
            correo="superadmin@nexusrh.pe",
            defaults={
                "empresa_id": None,
                "rol": rol,
                "codigo_unico": "SUPERADMIN01",
                "password_hash": password_service.hash(DEMO_PASSWORD),
                "estado": EstadosUsuario.ACTIVO,
                "estado_seguridad": EstadosSeguridadUsuario.NORMAL,
                "password_changed_at": timezone.now(),
            },
        )
        if creado:
            self.stdout.write("Superadmin creado: superadmin@nexusrh.pe")

    def _crear_empresa_completa(self, cfg, password_service):
        empresa = EmpresaModel.objects.create(
            ruc=cfg["ruc"],
            razon_social=cfg["razon_social"],
            nombre_comercial=cfg["nombre_comercial"],
            correo=f"contacto@{cfg['dominio']}",
            telefono=cfg["telefono"],
            direccion=cfg["direccion"],
            estado=EstadosEmpresa.ACTIVA,
        )

        sede = SedeModel.objects.create(
            empresa=empresa,
            nombre=cfg["sede"]["nombre"],
            direccion=cfg["direccion"],
            latitud=cfg["sede"]["lat"],
            longitud=cfg["sede"]["lon"],
            radio_metros=150,
            es_activa=True,
        )

        plan = PlanModel.objects.get(nombre=cfg["plan"])
        SuscripcionModel.objects.create(
            empresa_id=empresa.id,
            plan=plan,
            estado=EstadosSuscripcion.ACTIVA,
            fecha_inicio=timezone.now() - timedelta(days=60),
            fecha_proxima_facturacion=timezone.now() + timedelta(days=30),
            usuarios_activos=3,
        )

        rol_propietario = RolModel.objects.get(nombre=RolesUsuario.PROPIETARIO, empresa_id=None)
        rol_admin = RolModel.objects.get(nombre=RolesUsuario.ADMIN, empresa_id=None)
        rol_empleado = RolModel.objects.get(nombre=RolesUsuario.EMPLEADO, empresa_id=None)

        propietario_nombre, propietario_apellido = self._nombre_aleatorio()
        UsuarioModel.objects.create(
            empresa_id=empresa.id,
            rol=rol_propietario,
            codigo_unico=f"PROP-{cfg['slug']}-01",
            correo=f"{propietario_nombre.lower()}.{propietario_apellido.lower()}@{cfg['dominio']}",
            password_hash=password_service.hash(DEMO_PASSWORD),
            estado=EstadosUsuario.ACTIVO,
            estado_seguridad=EstadosSeguridadUsuario.NORMAL,
            password_changed_at=timezone.now(),
        )

        for i in range(1, 3):
            nombre, apellido = self._nombre_aleatorio()
            UsuarioModel.objects.create(
                empresa_id=empresa.id,
                rol=rol_admin,
                codigo_unico=f"ADM-{cfg['slug']}-{i:02d}",
                correo=f"{nombre.lower()}.{apellido.lower()}{i}@{cfg['dominio']}",
                password_hash=password_service.hash(DEMO_PASSWORD),
                estado=EstadosUsuario.ACTIVO,
                estado_seguridad=EstadosSeguridadUsuario.NORMAL,
                password_changed_at=timezone.now(),
            )

        self._crear_empleados(empresa, sede, cfg, rol_empleado, password_service)

        self.stdout.write(f"Empresa creada: {cfg['razon_social']} ({cfg['n_empleados']} empleados)")

    def _crear_empleados(self, empresa, sede, cfg, rol_empleado, password_service):
        dni_base = 70000000 + (empresa.id * 100000)
        empleados = []
        primer_empleado_con_login = None

        for i in range(1, cfg["n_empleados"] + 1):
            nombre, apellido1 = self._nombre_aleatorio()
            apellido2 = random.choice(APELLIDOS)
            area = random.choice(list(AREAS_CARGOS.keys()))
            cargo = random.choice(AREAS_CARGOS[area])
            codigo_unico = f"EMP-{cfg['slug']}-{i:04d}"
            correo = f"{nombre.lower()}.{apellido1.lower()}{i}@{cfg['dominio']}"
            fecha_ingreso = timezone.now().date() - timedelta(days=random.randint(30, 1500))

            usuario_id = None
            if i == 1:
                # Un empleado de ejemplo con acceso propio (rol EMPLEADO, app movil)
                usuario = UsuarioModel.objects.create(
                    empresa_id=empresa.id,
                    rol=rol_empleado,
                    codigo_unico=f"USREMP-{cfg['slug']}-01",
                    correo=f"appmovil.{correo}",
                    password_hash=password_service.hash(DEMO_PASSWORD),
                    estado=EstadosUsuario.ACTIVO,
                    estado_seguridad=EstadosSeguridadUsuario.NORMAL,
                    password_changed_at=timezone.now(),
                )
                usuario_id = usuario.id
                primer_empleado_con_login = correo

            empleados.append(EmpleadoModel(
                empresa_id=empresa.id,
                usuario_id=usuario_id,
                sede_id=sede.id,
                codigo_unico=codigo_unico,
                nombres=nombre,
                apellidos=f"{apellido1} {apellido2}",
                tipo_documento=TiposDocumento.DNI,
                numero_documento=str(dni_base + i),
                correo=correo,
                cargo=cargo,
                area=area,
                estado=EstadosEmpleado.ACTIVO,
                fecha_ingreso=fecha_ingreso,
            ))

        EmpleadoModel.objects.bulk_create(empleados)
        if primer_empleado_con_login:
            self.stdout.write(f"  Empleado con acceso app movil: appmovil.{primer_empleado_con_login}")

    def _nombre_aleatorio(self):
        if random.random() < 0.5:
            nombre = random.choice(NOMBRES_M)
        else:
            nombre = random.choice(NOMBRES_F)
        apellido = random.choice(APELLIDOS)
        return nombre, apellido
