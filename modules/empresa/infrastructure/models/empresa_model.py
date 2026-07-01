from django.db import models
from shared.constants import EstadosEmpresa


class EmpresaModel(models.Model):
    ruc = models.CharField(max_length=11, unique=True)
    razon_social = models.CharField(max_length=255)
    nombre_comercial = models.CharField(max_length=255)
    correo = models.EmailField()
    telefono = models.CharField(max_length=20)
    direccion = models.TextField()
    logo_url = models.TextField(null=True, blank=True)
    estado = models.CharField(
        max_length=20,
        choices=EstadosEmpresa.CHOICES,
        default=EstadosEmpresa.EN_PRUEBA,
    )
    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = "empresa"
        db_table = "empresas"
        ordering = ["-fecha_registro"]

    def __str__(self):
        return f"{self.ruc} - {self.razon_social}"