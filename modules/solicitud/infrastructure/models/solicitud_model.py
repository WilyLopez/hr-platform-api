from django.db import models
from shared.constants import EstadosSolicitud
from modules.solicitud.infrastructure.models.tipo_permiso_model import TipoPermisoModel


class SolicitudModel(models.Model):
    empresa_id = models.IntegerField()
    empleado_id = models.IntegerField()
    tipo_permiso = models.ForeignKey(TipoPermisoModel, on_delete=models.PROTECT, related_name="solicitudes")
    tipo_permiso_nombre = models.CharField(max_length=100)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    hora_inicio = models.TimeField(null=True, blank=True)
    hora_fin = models.TimeField(null=True, blank=True)
    motivo = models.TextField()
    estado = models.CharField(
        max_length=20,
        choices=EstadosSolicitud.CHOICES,
        default=EstadosSolicitud.PENDIENTE,
    )
    adjunto_url = models.URLField(null=True, blank=True)
    comentario_evaluador = models.TextField(null=True, blank=True)
    evaluado_por_id = models.IntegerField(null=True, blank=True)
    fecha_evaluacion = models.DateTimeField(null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = "solicitud"
        db_table = "solicitudes"
        indexes = [
            models.Index(fields=["empresa_id", "estado"]),
            models.Index(fields=["empleado_id", "estado"]),
            models.Index(fields=["fecha_inicio", "fecha_fin"]),
        ]

    def __str__(self):
        return f"Solicitud {self.id} - Empleado {self.empleado_id} - {self.estado}"