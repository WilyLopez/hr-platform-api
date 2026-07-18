from django.db import models
from shared.constants import EstadosUsuario
from modules.usuario.infrastructure.models.rol_model import RolModel


class UsuarioModel(models.Model):
    empresa_id = models.IntegerField(null=True, blank=True)
    rol = models.ForeignKey(RolModel, on_delete=models.PROTECT, related_name="usuarios")
    codigo_unico = models.CharField(max_length=20, unique=True)
    correo = models.EmailField(unique=True)
    password_hash = models.CharField(max_length=255)
    estado = models.CharField(
        max_length=20,
        choices=EstadosUsuario.CHOICES,
        default=EstadosUsuario.ACTIVO,
    )
    from shared.constants import EstadosSeguridadUsuario
    estado_seguridad = models.CharField(
        max_length=40,
        choices=EstadosSeguridadUsuario.CHOICES,
        default=EstadosSeguridadUsuario.NORMAL,
    )
    password_changed_at = models.DateTimeField(null=True, blank=True)
    intentos_fallidos = models.PositiveSmallIntegerField(default=0)
    ultimo_acceso = models.DateTimeField(null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = "usuario"
        db_table = "usuarios"
        indexes = [
            models.Index(fields=["empresa_id"]),
            models.Index(fields=["codigo_unico"]),
        ]

    def __str__(self):
        return self.correo