from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from shared.interfaces.base_serializer import BaseSerializer


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = "codigo_unico"

    codigo_unico = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        return attrs


class LoginSerializer(BaseSerializer):
    codigo_unico = serializers.CharField()
    contrasena = serializers.CharField(write_only=True)


class TokenSecuritySerializer(serializers.Serializer):
    must_change_password = serializers.BooleanField()


class TokenOutputSerializer(BaseSerializer):
    access = serializers.CharField()
    refresh = serializers.CharField()
    usuario_id = serializers.IntegerField()
    codigo_unico = serializers.CharField()
    empresa_id = serializers.IntegerField(allow_null=True)
    rol = serializers.CharField()
    security = TokenSecuritySerializer()


class RefrescarTokenSerializer(BaseSerializer):
    refresh = serializers.CharField()


class RecuperarContrasenaSerializer(BaseSerializer):
    correo = serializers.EmailField()


class CambiarContrasenaSerializer(BaseSerializer):
    contrasena_actual = serializers.CharField(write_only=True)
    contrasena_nueva = serializers.CharField(min_length=8, write_only=True)