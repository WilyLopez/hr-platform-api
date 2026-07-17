from rest_framework import serializers
from shared.interfaces.base_serializer import BaseSerializer


class CrearSolicitudSerializer(BaseSerializer):
    tipo_permiso_id = serializers.IntegerField()
    fecha_inicio = serializers.DateField()
    fecha_fin = serializers.DateField()
    hora_inicio = serializers.TimeField(format="%H:%M", required=False, allow_null=True)
    hora_fin = serializers.TimeField(format="%H:%M", required=False, allow_null=True)
    motivo = serializers.CharField(min_length=10)
    adjunto_url = serializers.URLField(required=False, allow_null=True)

    def validate(self, attrs):
        if attrs["fecha_fin"] < attrs["fecha_inicio"]:
            raise serializers.ValidationError(
                {"fecha_fin": "La fecha de fin no puede ser anterior a la fecha de inicio."}
            )
        if attrs.get("hora_inicio") and not attrs.get("hora_fin"):
            raise serializers.ValidationError({"hora_fin": "Debe especificar hora de fin si hay hora de inicio."})
        if attrs.get("hora_fin") and not attrs.get("hora_inicio"):
            raise serializers.ValidationError({"hora_inicio": "Debe especificar hora de inicio si hay hora de fin."})
        return attrs


class EvaluarSolicitudSerializer(BaseSerializer):
    comentario = serializers.CharField(required=False, allow_null=True, allow_blank=True)


class SolicitudOutputSerializer(BaseSerializer):
    id = serializers.IntegerField()
    empresa_id = serializers.IntegerField()
    empleado_id = serializers.IntegerField()
    empleado_nombre = serializers.CharField()
    tipo_permiso_id = serializers.IntegerField()
    tipo_permiso_nombre = serializers.CharField()
    fecha_inicio = serializers.DateField()
    fecha_fin = serializers.DateField()
    hora_inicio = serializers.TimeField(format="%H:%M", allow_null=True, required=False)
    hora_fin = serializers.TimeField(format="%H:%M", allow_null=True, required=False)
    dias_solicitados = serializers.IntegerField()
    motivo = serializers.CharField()
    estado = serializers.CharField()
    adjunto_url = serializers.URLField(allow_null=True)
    comentario_evaluador = serializers.CharField(allow_null=True)
    evaluado_por_id = serializers.IntegerField(allow_null=True)
    fecha_evaluacion = serializers.DateTimeField(allow_null=True)
    fecha_creacion = serializers.DateTimeField()