from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from modules.empleado.application.dtos.empleado_dto import (
    RegistrarEmpleadoInputDTO,
    ActualizarEmpleadoInputDTO,
    ListarEmpleadosInputDTO,
    AsignarSedeInputDTO,
)
from modules.empleado.interfaces.serializers.empleado_serializer import (
    RegistrarEmpleadoSerializer,
    ActualizarEmpleadoSerializer,
    AsignarSedeSerializer,
    EmpleadoOutputSerializer,
)
from modules.empleado.infrastructure.repositories.empleado_repository_impl import DjangoEmpleadoRepository
from modules.empresa.infrastructure.repositories.sede_repository_impl import DjangoSedeRepository
from modules.empleado.application.use_cases.registrar_empleado import RegistrarEmpleadoUseCase
from modules.empleado.application.use_cases.actualizar_empleado import ActualizarEmpleadoUseCase
from modules.empleado.application.use_cases.desactivar_empleado import DesactivarEmpleadoUseCase
from modules.empleado.application.use_cases.reactivar_empleado import ReactivarEmpleadoUseCase
from modules.empleado.application.use_cases.listar_empleados import ListarEmpleadosUseCase
from modules.empleado.application.use_cases.asignar_sede import AsignarSedeUseCase
from modules.auditoria.infrastructure.repositories.auditoria_repository_impl import DjangoAuditoriaRepository
from modules.auditoria.application.use_cases.registrar_evento import RegistrarEventoUseCase
from modules.suscripcion.infrastructure.repositories.suscripcion_repository_impl import DjangoSuscripcionRepository
from modules.suscripcion.application.use_cases.verificar_limites import VerificarLimitesUseCase


def _auditoria():
    return RegistrarEventoUseCase(DjangoAuditoriaRepository())


class EmpleadoListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        empresa_id = request.empresa_id
        input_dto = ListarEmpleadosInputDTO(
            empresa_id=empresa_id,
            estado=request.query_params.get("estado"),
            area=request.query_params.get("area"),
            sede_id=request.query_params.get("sede_id"),
            search=request.query_params.get("search"),
            page=int(request.query_params.get("page", 1)),
            page_size=int(request.query_params.get("page_size", 20)),
        )
        outputs = ListarEmpleadosUseCase(DjangoEmpleadoRepository()).execute(input_dto)
        return Response(EmpleadoOutputSerializer(outputs, many=True).data)

    def post(self, request):
        serializer = RegistrarEmpleadoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        d = serializer.validated_data

        class _SuscAdapter:
            def verificar_limites(self, eid):
                VerificarLimitesUseCase(DjangoSuscripcionRepository()).execute(eid)

            def incrementar_usuario(self, _):
                pass

        class _UsuAdapter:
            def crear_empleado(self, empresa_id, correo, codigo_unico):
                from modules.usuario.application.use_cases.crear_usuario import CrearUsuarioUseCase
                from modules.usuario.application.dtos.usuario_dto import CrearUsuarioInputDTO
                from modules.usuario.infrastructure.repositories.usuario_repository_impl import DjangoUsuarioRepository
                from modules.usuario.infrastructure.repositories.rol_repository_impl import DjangoRolRepository
                from modules.usuario.infrastructure.services.jwt_service import PasswordService
                import secrets, string
                contrasena = "".join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))
                uc = CrearUsuarioUseCase(
                    DjangoUsuarioRepository(), DjangoRolRepository(), PasswordService(), _auditoria()
                )
                return uc.execute(CrearUsuarioInputDTO(
                    empresa_id=empresa_id, rol_nombre="EMPLEADO",
                    correo=correo, contrasena=contrasena,
                ))

        class _NotifAdapter:
            def notificar_bienvenida_empleado(self, correo, codigo_unico):
                from modules.notificacion.infrastructure.services.email_service import EmailService
                EmailService().notificar_bienvenida_empleado(correo, codigo_unico)

        use_case = RegistrarEmpleadoUseCase(
            empleado_repository=DjangoEmpleadoRepository(),
            suscripcion_use_case=_SuscAdapter(),
            usuario_use_case=_UsuAdapter(),
            auditoria_use_case=_auditoria(),
            notificacion_use_case=_NotifAdapter(),
        )
        output = use_case.execute(RegistrarEmpleadoInputDTO(
            empresa_id=request.empresa_id, **d
        ))
        return Response(EmpleadoOutputSerializer(output).data, status=status.HTTP_201_CREATED)


class EmpleadoDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, empleado_id):
        from modules.empleado.domain.exceptions import EmpleadoNoEncontradoException
        from modules.empleado.application.dtos.empleado_dto import EmpleadoOutputDTO
        empleado = DjangoEmpleadoRepository().get_by_id(empleado_id)
        if not empleado or empleado.empresa_id != request.empresa_id:
            raise EmpleadoNoEncontradoException(str(empleado_id))
        output = EmpleadoOutputDTO(
            id=empleado.id, empresa_id=empleado.empresa_id,
            codigo_unico=str(empleado.codigo_unico),
            nombres=empleado.nombres, apellidos=empleado.apellidos,
            tipo_documento=empleado.documento.tipo,
            numero_documento=empleado.documento.value,
            correo=str(empleado.correo), cargo=empleado.cargo,
            area=empleado.area, sede_id=empleado.sede_id,
            sede_nombre=None, estado=empleado.estado,
            fecha_ingreso=empleado.fecha_ingreso,
            fecha_creacion=empleado.fecha_creacion,
        )
        return Response(EmpleadoOutputSerializer(output).data)

    def patch(self, request, empleado_id):
        serializer = ActualizarEmpleadoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        use_case = ActualizarEmpleadoUseCase(DjangoEmpleadoRepository(), _auditoria())
        output = use_case.execute(ActualizarEmpleadoInputDTO(
            empleado_id=empleado_id, empresa_id=request.empresa_id,
            **serializer.validated_data,
        ))
        return Response(EmpleadoOutputSerializer(output).data)


class EmpleadoDesactivarView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, empleado_id):
        class _SuscAdapter:
            def decrementar_usuario(self, _):
                pass

        DesactivarEmpleadoUseCase(DjangoEmpleadoRepository(), _SuscAdapter()).execute({
            "empleado_id": empleado_id,
            "empresa_id": request.empresa_id,
        })
        return Response({"status": "ok"})


class EmpleadoReactivarView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, empleado_id):
        class _SuscAdapter:
            def verificar_limites(self, eid):
                VerificarLimitesUseCase(DjangoSuscripcionRepository()).execute(eid)

            def incrementar_usuario(self, _):
                pass

        ReactivarEmpleadoUseCase(DjangoEmpleadoRepository(), _SuscAdapter()).execute({
            "empleado_id": empleado_id,
            "empresa_id": request.empresa_id,
        })
        return Response({"status": "ok"})


class EmpleadoSedeView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, empleado_id):
        serializer = AsignarSedeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        AsignarSedeUseCase(DjangoEmpleadoRepository(), DjangoSedeRepository()).execute(
            AsignarSedeInputDTO(
                empleado_id=empleado_id,
                empresa_id=request.empresa_id,
                sede_id=serializer.validated_data["sede_id"],
            )
        )
        return Response({"status": "ok"})