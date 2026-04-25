from rest_framework import serializers


class BaseModelSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        return {k: v for k, v in representation.items() if v is not None}


class BaseSerializer(serializers.Serializer):
    def create(self, validated_data):
        raise NotImplementedError

    def update(self, instance, validated_data):
        raise NotImplementedError