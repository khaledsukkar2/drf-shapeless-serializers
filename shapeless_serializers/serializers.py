from rest_framework import serializers

from shapeless_serializers.mixins import (
    DynamicConditionalFieldsMixin,
    DynamicFieldAttributesMixin,
    DynamicFieldRenamingMixin,
    DynamicFieldsMixin,
    DynamicNestedSerializerMixin,
)


class ShapelessSerializer(
    DynamicFieldsMixin,
    DynamicFieldAttributesMixin,
    DynamicNestedSerializerMixin,
    DynamicFieldRenamingMixin,
    DynamicConditionalFieldsMixin,
    serializers.Serializer,
):
    pass


class ShapelessModelSerializer(
    DynamicFieldsMixin,
    DynamicFieldAttributesMixin,
    DynamicFieldRenamingMixin,
    DynamicNestedSerializerMixin,
    DynamicConditionalFieldsMixin,
    serializers.ModelSerializer,
):
    pass


class ShapelessHyperlinkedModelSerializer(serializers.HyperlinkedModelSerializer):
    pass
