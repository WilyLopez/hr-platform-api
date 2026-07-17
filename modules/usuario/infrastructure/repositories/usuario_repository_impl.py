from typing import Optional, List
from shared.domain.value_objects import Email, CodigoUnico
from shared.constants import EstadosUsuario
from modules.usuario.domain.entities.usuario import Usuario
from modules.usuario.domain.repositories.usuario_repository import UsuarioRepository
from modules.usuario.infrastructure.models.usuario_model import UsuarioModel


class DjangoUsuarioRepository(UsuarioRepository):
    def get_by_id(self, id: int) -> Optional[Usuario]:
        try:
            return self._to_entity(UsuarioModel.objects.get(pk=id))
        except UsuarioModel.DoesNotExist:
            return None

    def get_by_codigo_unico(self, codigo: str) -> Optional[Usuario]:
        try:
            return self._to_entity(UsuarioModel.objects.get(codigo_unico=codigo))
        except UsuarioModel.DoesNotExist:
            return None

    def get_by_correo(self, correo: str) -> Optional[Usuario]:
        try:
            return self._to_entity(UsuarioModel.objects.get(correo=correo))
        except UsuarioModel.DoesNotExist:
            return None

    def get_by_empresa(self, empresa_id: int, rol: Optional[str] = None) -> List[Usuario]:
        qs = UsuarioModel.objects.filter(empresa_id=empresa_id)
        if rol:
            qs = qs.filter(rol__nombre=rol)
        return [self._to_entity(m) for m in qs]

    def save(self, usuario: Usuario) -> Usuario:
        if usuario.id:
            model = UsuarioModel.objects.get(pk=usuario.id)
        else:
            model = UsuarioModel()

        model.empresa_id = usuario.empresa_id
        model.rol_id = usuario.rol_id
        model.codigo_unico = str(usuario.codigo_unico)
        model.correo = str(usuario.correo)
        model.password_hash = usuario.password_hash
        model.estado = usuario.estado
        model.estado_seguridad = usuario.estado_seguridad
        model.password_changed_at = usuario.password_changed_at
        model.intentos_fallidos = usuario.intentos_fallidos
        model.ultimo_acceso = usuario.ultimo_acceso
        model.fecha_actualizacion = usuario.fecha_actualizacion
        model.save()

        usuario.id = model.pk
        return usuario

    def exists_by_correo(self, correo: str) -> bool:
        return UsuarioModel.objects.filter(correo=correo).exists()

    def exists_by_codigo_unico(self, codigo: str) -> bool:
        return UsuarioModel.objects.filter(codigo_unico=codigo).exists()

    def count_activos_by_empresa(self, empresa_id: int) -> int:
        return UsuarioModel.objects.filter(
            empresa_id=empresa_id, estado=EstadosUsuario.ACTIVO
        ).count()

    def _to_entity(self, model: UsuarioModel) -> Usuario:
        return Usuario(
            id=model.pk,
            empresa_id=model.empresa_id,
            rol_id=model.rol_id,
            codigo_unico=CodigoUnico(model.codigo_unico),
            correo=Email(model.correo),
            password_hash=model.password_hash,
            estado=model.estado,
            estado_seguridad=model.estado_seguridad,
            password_changed_at=model.password_changed_at,
            intentos_fallidos=model.intentos_fallidos,
            ultimo_acceso=model.ultimo_acceso,
            fecha_creacion=model.fecha_creacion,
            fecha_actualizacion=model.fecha_actualizacion,
        )