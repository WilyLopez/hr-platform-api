from rest_framework import serializers
from shared.interfaces.base_serializer import BaseSerializer


class RegistrarEmpresaSerializer(BaseSerializer):
    ruc = serializers.CharField(min_length=11, max_length=11)
    correo = serializers.EmailField()
    telefono = serializers.CharField(max_length=20)
    direccion = serializers.CharField()
    contrasena = serializers.CharField(min_length=8, write_only=True)
    plan_id = serializers.IntegerField()


class ActualizarEmpresaSerializer(BaseSerializer):
    nombre_comercial = serializers.CharField(max_length=255)
    telefono = serializers.CharField(max_length=20)
    direccion = serializers.CharField()
    logo_url = serializers.CharField(required=False, allow_null=True, allow_blank=True)


class EmpresaOutputSerializer(BaseSerializer):
    id = serializers.IntegerField()
    ruc = serializers.CharField()
    razon_social = serializers.CharField()
    nombre_comercial = serializers.CharField()
    correo = serializers.EmailField()
    telefono = serializers.CharField()
    direccion = serializers.CharField()
    logo_url = serializers.CharField(allow_null=True, allow_blank=True)
    estado = serializers.CharField()
    fecha_registro = serializers.DateTimeField()


class EmpresaListOutputSerializer(BaseSerializer):
    id = serializers.IntegerField()
    ruc = serializers.CharField()
    razon_social = serializers.CharField()
    estado = serializers.CharField()
    plan_nombre = serializers.CharField(allow_null=True)
    fecha_registro = serializers.DateTimeField()