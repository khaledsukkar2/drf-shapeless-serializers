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
    def __init__(self, *args, **kwargs):
        self._field_validators = kwargs.pop('field_validators', {})
        self._dynamic_validators = kwargs.pop('validators', None)
        super().__init__(*args, **kwargs)

        for field_name, validators in self._field_validators.items():
            if field_name in self.fields:
                self.fields[field_name].validators += validators

        if self._dynamic_validators is not None:
            self.Meta.validators = self._dynamic_validators


class ShapelessHyperlinkedModelSerializer(serializers.HyperlinkedModelSerializer):
    pass
