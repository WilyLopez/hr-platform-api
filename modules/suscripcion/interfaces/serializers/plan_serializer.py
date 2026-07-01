from rest_framework import serializers
from shared.interfaces.base_serializer import BaseSerializer
from shared.constants import PlanesNombre


class CrearPlanSerializer(BaseSerializer):
    nombre = serializers.CharField(max_length=100)
    precio_mensual = serializers.FloatField(min_value=0)
    limite_usuarios = serializers.IntegerField(min_value=1)
    almacenamiento_gb = serializers.IntegerField(min_value=1)
    color = serializers.CharField(max_length=7, required=False, default="#3b82f6")
    descripcion_corta = serializers.CharField(max_length=150, required=False, allow_null=True, allow_blank=True)
    orden = serializers.IntegerField(min_value=0, required=False, default=0)
    es_activo = serializers.BooleanField(required=False, default=True)

class ActualizarPlanSerializer(BaseSerializer):
    precio_mensual = serializers.FloatField(min_value=0)
    limite_usuarios = serializers.IntegerField(min_value=1)
    almacenamiento_gb = serializers.IntegerField(min_value=1)
    color = serializers.CharField(max_length=7, required=False, default="#3b82f6")
    descripcion_corta = serializers.CharField(max_length=150, required=False, allow_null=True, allow_blank=True)
    orden = serializers.IntegerField(min_value=0, required=False, default=0)
    es_activo = serializers.BooleanField(required=False, default=True)


class PlanOutputSerializer(BaseSerializer):
    id = serializers.IntegerField()
    nombre = serializers.CharField()
    precio_mensual = serializers.FloatField()
    limite_usuarios = serializers.IntegerField()
    almacenamiento_gb = serializers.IntegerField()
    color = serializers.CharField()
    descripcion_corta = serializers.CharField(allow_null=True)
    orden = serializers.IntegerField()
    es_activo = serializers.BooleanField()
    empresas_count = serializers.IntegerField(required=False)