from rest_framework import serializers
from shared.interfaces.base_serializer import BaseSerializer

class AsignarHorarioSerializer(BaseSerializer):
    empleado_id = serializers.IntegerField(min_value=1)
    horario_id = serializers.IntegerField(min_value=1)
    fecha_desde = serializers.DateField()
    fecha_hasta = serializers.DateField(required=False, allow_null=True)

class AsignacionOutputSerializer(BaseSerializer):
    id = serializers.IntegerField()
    empleado_id = serializers.IntegerField()
    horario_id = serializers.IntegerField()
    horario_nombre = serializers.CharField()
    fecha_desde = serializers.DateField()
    fecha_hasta = serializers.DateField(required=False, allow_null=True)
    fecha_creacion = serializers.DateTimeField()
