from django.db import models


class HorarioModel(models.Model):
    empresa = models.ForeignKey(
        "empresa.EmpresaModel", on_delete=models.CASCADE, related_name="horarios"
    )
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True, null=True)
    es_activo = models.BooleanField(default=True)
    tolerancia_ingreso_min = models.PositiveIntegerField(default=15)
    tolerancia_salida_min = models.PositiveIntegerField(default=0)
    horas_extras_permitidas = models.BooleanField(default=False)
    max_horas_extras_dia = models.PositiveIntegerField(default=0)
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = "horario"
        db_table = "horarios"

    def __str__(self):
        return f"{self.nombre} ({self.empresa_id})"


class TurnoModel(models.Model):
    horario = models.ForeignKey(
        HorarioModel, on_delete=models.CASCADE, related_name="turnos"
    )
    dia_semana = models.SmallIntegerField()  # 0=Lunes, 6=Domingo
    hora_inicio = models.TimeField(null=True, blank=True)
    hora_fin = models.TimeField(null=True, blank=True)
    minutos_refrigerio = models.PositiveIntegerField(default=0)
    es_laborable = models.BooleanField(default=True)

    class Meta:
        app_label = "horario"
        db_table = "horarios_turnos"
        unique_together = ("horario", "dia_semana")


class AsignacionHorarioModel(models.Model):
    empleado = models.ForeignKey(
        "empleado.EmpleadoModel", on_delete=models.CASCADE, related_name="asignaciones_horario"
    )
    horario = models.ForeignKey(
        HorarioModel, on_delete=models.PROTECT, related_name="asignaciones"
    )
    fecha_desde = models.DateField()
    fecha_hasta = models.DateField(null=True, blank=True)
    creado_por = models.ForeignKey(
        "usuario.UsuarioModel", on_delete=models.SET_NULL, null=True, blank=True
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "horario"
        db_table = "horarios_asignaciones"
