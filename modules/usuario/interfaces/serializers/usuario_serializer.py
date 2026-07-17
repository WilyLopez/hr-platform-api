from rest_framework import serializers
from shared.interfaces.base_serializer import BaseSerializer
from shared.constants import RolesUsuario


class CrearUsuarioSerializer(BaseSerializer):
    empresa_id = serializers.IntegerField(required=False, allow_null=True)
    rol_nombre = serializers.ChoiceField(choices=RolesUsuario.CHOICES)
    correo = serializers.EmailField()
    contrasena = serializers.CharField(min_length=8, write_only=True)


class ActualizarUsuarioSerializer(BaseSerializer):
    correo = serializers.EmailField(required=False)


class UsuarioOutputSerializer(BaseSerializer):
    id = serializers.IntegerField()
    empresa_id = serializers.IntegerField(allow_null=True)
    codigo_unico = serializers.CharField()
    correo = serializers.EmailField()
    rol = serializers.CharField()
    estado = serializers.CharField()
    ultimo_acceso = serializers.DateTimeField(allow_null=True)
    fecha_creacion = serializers.DateTimeField()
    nombre_completo = serializers.CharField(required=False, allow_null=True)


class AsignarRolSerializer(BaseSerializer):
    rol_id = serializers.IntegerField()