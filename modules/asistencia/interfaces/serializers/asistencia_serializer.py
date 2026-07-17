from rest_framework import serializers
from shared.interfaces.base_serializer import BaseSerializer
from shared.constants import TiposMarcaje, OrigenMarcaje


class RegistrarMarcajeSerializer(BaseSerializer):
    origen = serializers.ChoiceField(choices=OrigenMarcaje.CHOICES)
    token_qr = serializers.CharField(required=False, allow_null=True)
    latitud = serializers.FloatField(min_value=-90, max_value=90, required=False, allow_null=True)
    longitud = serializers.FloatField(min_value=-180, max_value=180, required=False, allow_null=True)


class RegistrarManualSerializer(BaseSerializer):
    empleado_id = serializers.IntegerField()
    tipo = serializers.ChoiceField(choices=TiposMarcaje.CHOICES)
    fecha = serializers.DateField()
    hora = serializers.TimeField(format="%H:%M")
    justificacion = serializers.CharField(min_length=10)


class RegistroAsistenciaOutputSerializer(BaseSerializer):
    id = serializers.IntegerField()
    empleado_id = serializers.IntegerField()
    empleado_nombre = serializers.CharField()
    sede_id = serializers.IntegerField()
    sede_nombre = serializers.CharField(allow_null=True)
    tipo = serializers.CharField()
    origen = serializers.CharField()
    estado_auditoria = serializers.CharField()
    resultado = serializers.CharField()
    minutos_tardanza = serializers.IntegerField()
    minutos_extra = serializers.IntegerField()
    minutos_temprano = serializers.IntegerField()
    horas_trabajadas = serializers.FloatField()
    estado_extras = serializers.CharField(allow_null=True, required=False)
    minutos_extra_aprobados = serializers.IntegerField(allow_null=True, required=False)
    timestamp = serializers.DateTimeField()


class ReporteAsistenciaOutputSerializer(BaseSerializer):
    empleado_id = serializers.IntegerField()
    empleado_nombre = serializers.CharField()
    total_dias = serializers.IntegerField()
    dias_presentes = serializers.IntegerField()
    dias_ausentes = serializers.IntegerField()
    tardanzas = serializers.IntegerField()
    registros = RegistroAsistenciaOutputSerializer(many=True)


class EstadoAsistenciaHoySerializer(BaseSerializer):
    estado_actual = serializers.CharField()
    horario_hoy = serializers.CharField()
    ultimo_marcaje = serializers.CharField(allow_null=True)
    tiempo_trabajado_str = serializers.CharField()
    tiempo_trabajado_minutos = serializers.IntegerField()