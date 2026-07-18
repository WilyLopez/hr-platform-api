from rest_framework import serializers
from shared.interfaces.base_serializer import BaseSerializer
from datetime import time

class TurnoInputSerializer(BaseSerializer):
    dia_semana = serializers.IntegerField(min_value=0, max_value=6)
    hora_inicio = serializers.TimeField(required=False, allow_null=True)
    hora_fin = serializers.TimeField(required=False, allow_null=True)
    minutos_refrigerio = serializers.IntegerField(min_value=0, default=0)
    es_laborable = serializers.BooleanField(default=True)

class CrearHorarioSerializer(BaseSerializer):
    nombre = serializers.CharField(max_length=150)
    descripcion = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    tolerancia_ingreso_min = serializers.IntegerField(min_value=0, default=15)
    tolerancia_salida_min = serializers.IntegerField(min_value=0, default=0)
    horas_extras_permitidas = serializers.BooleanField(default=False)
    max_horas_extras_dia = serializers.IntegerField(min_value=0, default=0)
    turnos = TurnoInputSerializer(many=True, allow_empty=False)

class ActualizarHorarioSerializer(CrearHorarioSerializer):
    es_activo = serializers.BooleanField(default=True)

class TurnoOutputSerializer(BaseSerializer):
    id = serializers.IntegerField()
    horario_id = serializers.IntegerField()
    dia_semana = serializers.IntegerField()
    hora_inicio = serializers.TimeField(required=False, allow_null=True)
    hora_fin = serializers.TimeField(required=False, allow_null=True)
    minutos_refrigerio = serializers.IntegerField()
    es_laborable = serializers.BooleanField()

class HorarioOutputSerializer(BaseSerializer):
    id = serializers.IntegerField()
    nombre = serializers.CharField()
    descripcion = serializers.CharField(allow_null=True)
    es_activo = serializers.BooleanField()
    tolerancia_ingreso_min = serializers.IntegerField()
    tolerancia_salida_min = serializers.IntegerField()
    horas_extras_permitidas = serializers.BooleanField()
    max_horas_extras_dia = serializers.IntegerField()
    turnos = TurnoOutputSerializer(many=True)
    empleados_asignados = serializers.IntegerField(required=False, allow_null=True)
