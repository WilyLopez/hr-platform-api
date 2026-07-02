from django.db import models
from shared.constants import PlanesNombre


class PlanModel(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    precio_mensual = models.DecimalField(max_digits=10, decimal_places=2)
    limite_usuarios = models.PositiveIntegerField()
    almacenamiento_gb = models.PositiveIntegerField()
    color = models.CharField(max_length=7, default="#3b82f6")
    descripcion_corta = models.CharField(max_length=150, blank=True, null=True)
    orden = models.PositiveIntegerField(default=0)
    es_activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = "suscripcion"
        db_table = "planes"

    def __str__(self):
        return self.nombre