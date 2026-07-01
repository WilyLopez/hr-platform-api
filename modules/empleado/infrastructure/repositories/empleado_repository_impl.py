from typing import Optional, List
from django.db.models import Q
from shared.domain.value_objects import Email, CodigoUnico, NumeroDocumento
from shared.constants import EstadosEmpleado
from modules.empleado.domain.entities.empleado import Empleado
from modules.empleado.domain.repositories.empleado_repository import EmpleadoRepository
from modules.empleado.infrastructure.models.empleado_model import EmpleadoModel


class DjangoEmpleadoRepository(EmpleadoRepository):
    def get_by_id(self, id: int) -> Optional[Empleado]:
        try:
            return self._to_entity(EmpleadoModel.objects.get(pk=id))
        except EmpleadoModel.DoesNotExist:
            return None

    def get_by_codigo_unico(self, codigo: str) -> Optional[Empleado]:
        try:
            return self._to_entity(EmpleadoModel.objects.get(codigo_unico=codigo))
        except EmpleadoModel.DoesNotExist:
            return None

    def exists_by_codigo_unico(self, codigo: str) -> bool:
        return EmpleadoModel.objects.filter(codigo_unico=codigo).exists()

    def get_by_empresa(
        self,
        empresa_id: int,
        estado: Optional[str] = None,
        area: Optional[str] = None,
        sede_id: Optional[int] = None,
        search: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> List[Empleado]:
        qs = EmpleadoModel.objects.filter(empresa_id=empresa_id)
        if estado:
            qs = qs.filter(estado=estado)
        if area:
            qs = qs.filter(area__iexact=area)
        if sede_id:
            qs = qs.filter(sede_id=sede_id)
        if search:
            qs = qs.filter(
                Q(nombres__icontains=search)
                | Q(apellidos__icontains=search)
                | Q(codigo_unico__icontains=search)
                | Q(numero_documento__icontains=search)
            )
        offset = (page - 1) * page_size
        return [self._to_entity(m) for m in qs[offset: offset + page_size]]

    def save(self, empleado: Empleado) -> Empleado:
        if empleado.id:
            model = EmpleadoModel.objects.get(pk=empleado.id)
        else:
            model = EmpleadoModel()

        model.empresa_id = empleado.empresa_id
        model.usuario_id = empleado.usuario_id
        model.sede_id = empleado.sede_id
        model.codigo_unico = str(empleado.codigo_unico)
        model.nombres = empleado.nombres
        model.apellidos = empleado.apellidos
        model.tipo_documento = empleado.documento.tipo
        model.numero_documento = empleado.documento.value
        model.correo = str(empleado.correo)
        model.cargo = empleado.cargo
        model.area = empleado.area
        model.estado = empleado.estado
        model.fecha_ingreso = empleado.fecha_ingreso
        model.fecha_actualizacion = empleado.fecha_actualizacion
        model.save()

        empleado.id = model.pk
        return empleado

    def exists_by_documento(self, empresa_id: int, numero_documento: str) -> bool:
        return EmpleadoModel.objects.filter(
            empresa_id=empresa_id, numero_documento=numero_documento
        ).exists()

    def exists_by_correo(self, empresa_id: int, correo: str) -> bool:
        return EmpleadoModel.objects.filter(empresa_id=empresa_id, correo=correo).exists()

    def count_activos_by_empresa(self, empresa_id: int) -> int:
        return EmpleadoModel.objects.filter(
            empresa_id=empresa_id, estado=EstadosEmpleado.ACTIVO
        ).count()

    def count_by_empresa(self, empresa_id: int, estado: Optional[str] = None) -> int:
        qs = EmpleadoModel.objects.filter(empresa_id=empresa_id)
        if estado:
            qs = qs.filter(estado=estado)
        return qs.count()

    def _to_entity(self, model: EmpleadoModel) -> Empleado:
        return Empleado(
            id=model.pk,
            empresa_id=model.empresa_id,
            usuario_id=model.usuario_id,
            codigo_unico=CodigoUnico(model.codigo_unico),
            nombres=model.nombres,
            apellidos=model.apellidos,
            documento=NumeroDocumento(model.numero_documento, model.tipo_documento),
            correo=Email(model.correo),
            cargo=model.cargo,
            area=model.area,
            sede_id=model.sede_id,
            estado=model.estado,
            fecha_ingreso=model.fecha_ingreso,
            fecha_creacion=model.fecha_creacion,
            fecha_actualizacion=model.fecha_actualizacion,
        )