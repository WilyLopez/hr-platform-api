from django.db import models
from shared.constants import TiposMarcaje, OrigenMarcaje, EstadosAuditoriaMarcaje, ResultadosMarcaje, EstadosHorasExtras


class RegistroAsistenciaModel(models.Model):
    empresa_id = models.IntegerField()
    empleado_id = models.IntegerField()
    sede_id = models.IntegerField()
    tipo = models.CharField(max_length=20, choices=TiposMarcaje.CHOICES)
    origen = models.CharField(max_length=15, choices=OrigenMarcaje.CHOICES, default=OrigenMarcaje.WEB)
    nivel_confianza = models.IntegerField(default=100)  # 0-100
    latitud = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitud = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    
    estado_auditoria = models.CharField(max_length=25, choices=EstadosAuditoriaMarcaje.CHOICES, default=EstadosAuditoriaMarcaje.VALIDO)
    resultado = models.CharField(max_length=20, choices=ResultadosMarcaje.CHOICES, default=ResultadosMarcaje.NORMAL)
    
    minutos_tardanza = models.IntegerField(default=0)
    minutos_extra = models.IntegerField(default=0)
    minutos_temprano = models.IntegerField(default=0)
    horas_trabajadas = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    
    # Horas Extras fields
    estado_extras = models.CharField(max_length=20, choices=EstadosHorasExtras.CHOICES, default=EstadosHorasExtras.NO_REQUIERE)
    minutos_extra_aprobados = models.IntegerField(default=0)
    extras_evaluado_por_id = models.IntegerField(null=True, blank=True)
    extras_fecha_evaluacion = models.DateTimeField(null=True, blank=True)
    extras_comentario = models.TextField(null=True, blank=True)
    enviado_a_nomina = models.BooleanField(default=False)
    
    observaciones = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "asistencia"
        db_table = "registros_asistencia"
        indexes = [
            models.Index(fields=["empleado_id", "timestamp"]),
            models.Index(fields=["empresa_id", "timestamp"]),
            models.Index(fields=["sede_id"]),
        ]

    def __str__(self):
        return f"Empleado {self.empleado_id} - {self.tipo} - {self.timestamp}"