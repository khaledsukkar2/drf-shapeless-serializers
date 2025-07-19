import sys
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union

from django.db import models

from shapeless_serializers.exceptions import (
    DynamicSerializerConfigError,
    ExcessiveNestingError,
)

##TODO write readme and how to contribute files
##TODO build the package and share it


class DynamicSerializerBaseMixin:
    """Base mixin for dynamic serializer functionality."""

    def __init__(self, *args, **kwargs):
        """Initialize the dynamic serializer base mixin."""
        self._context = kwargs.get("context", {})
        super().__init__(*args, **kwargs)


class DynamicFieldsMixin(DynamicSerializerBaseMixin):
    """Mixin to dynamically control which fields are included."""

    def __init__(self, *args, **kwargs):
        """Initialize with fields configuration."""
        self._fields = kwargs.pop("fields", None)
        super().__init__(*args, **kwargs)
        self._apply_dynamic_fields()

    def _apply_dynamic_fields(self) -> None:
        """Filter fields based on dynamic configuration."""
        if self._fields is None:
            return

        if not isinstance(self._fields, (list, tuple, set)):
            raise DynamicSerializerConfigError("'fields' must be a list, tuple, or set")

        allowed_fields = set(self._fields)
        existing_fields = set(self.fields.keys())

        for field_name in existing_fields - allowed_fields:
            self.fields.pop(field_name, None)


class DynamicFieldAttributesMixin(DynamicSerializerBaseMixin):
    """Mixin to dynamically set field attributes."""

    def __init__(self, *args, **kwargs):
        """Initialize with field_attributes configuration."""
        self._field_attributes = kwargs.pop("field_attributes", None)
        super().__init__(*args, **kwargs)
        self._apply_dynamic_field_attributes()

    def _apply_dynamic_field_attributes(self) -> None:
        """Apply dynamic attributes to fields."""
        if not self._field_attributes:
            return

        if not isinstance(self._field_attributes, dict):
            raise DynamicSerializerConfigError(
                "'field_attributes' must be a dictionary"
            )

        for field_name, attributes in self._field_attributes.items():
            if field_name not in self.fields:
                continue

            if not isinstance(attributes, dict):
                raise DynamicSerializerConfigError(
                    f"Attributes for field '{field_name}' must be a dictionary"
                )

            try:
                self._apply_attributes_to_field(
                    self.fields[field_name], attributes, self.instance, self._context
                )
            except Exception as e:
                raise DynamicSerializerConfigError(
                    f"Error applying attributes to field '{field_name}': {str(e)}"
                )

    def _apply_attributes_to_field(
        self,
        field_instance: Any,
        attributes: Dict[str, Any],
        instance: Any,
        context: Dict[str, Any],
    ) -> None:
        """Apply attributes to a single field instance."""
        for attr_name, attr_value in attributes.items():
            if not hasattr(field_instance, attr_name):
                raise AttributeError(f"Field has no attribute '{attr_name}'")

            resolved_value = (
                attr_value(instance, context) if callable(attr_value) else attr_value
            )
            setattr(field_instance, attr_name, resolved_value)


class DynamicFieldRenamingMixin(DynamicSerializerBaseMixin):
    """Mixin to dynamically rename fields in output."""

    def __init__(self, *args, **kwargs):
        """Initialize with rename_fields configuration."""
        self._rename_fields = kwargs.pop("rename_fields", None)
        super().__init__(*args, **kwargs)

    def to_representation(self, instance: Any) -> Dict[str, Any]:
        """Apply field renaming to representation."""
        representation = super().to_representation(instance)
        return self._apply_dynamic_renaming(representation)

    def _apply_dynamic_renaming(self, representation: Dict[str, Any]) -> Dict[str, Any]:
        """Process field renaming configuration."""
        if not self._rename_fields:
            return representation

        if not isinstance(self._rename_fields, dict):
            raise DynamicSerializerConfigError("'rename_fields' must be a dictionary")

        for old_name, new_name in self._rename_fields.items():
            if old_name in representation:
                representation[new_name] = representation.pop(old_name)

        return representation


class DynamicConditionalFieldsMixin(DynamicSerializerBaseMixin):
    """Mixin to dynamically include/exclude fields based on conditions."""

    def __init__(self, *args, **kwargs):
        """Initialize with conditional_fields configuration."""
        self._conditional_fields = kwargs.pop("conditional_fields", None)
        super().__init__(*args, **kwargs)

    def to_representation(self, instance: Any) -> Dict[str, Any]:
        """Apply conditional field filtering to representation."""
        representation = super().to_representation(instance)
        return self._apply_conditional_fields(instance, representation)

    def _apply_conditional_fields(
        self, instance: Any, representation: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process conditional fields configuration."""
        if not self._conditional_fields:
            return representation

        if not isinstance(self._conditional_fields, dict):
            raise DynamicSerializerConfigError(
                "'conditional_fields' must be a dictionary"
            )

        for field_name in list(representation.keys()):
            condition = self._conditional_fields.get(field_name)

            if condition is None:
                continue
            try:

                should_include = (
                    condition(instance, self._context)
                    if callable(condition)
                    else bool(condition)
                )
                if not should_include:
                    representation.pop(field_name)

            except Exception as e:
                raise DynamicSerializerConfigError(
                    f"Error evaluating condition for field '{field_name}': {str(e)}"
                )

        return representation


class DynamicNestedSerializerMixin(DynamicSerializerBaseMixin):
    """Enhanced mixin with proper handling of serializer params with recursion approach"""

    MAX_DEPTH = 100

    def __init__(self, *args, **kwargs):
        self._nested = kwargs.pop("nested", None)
        self._nesting_level = kwargs.pop("nesting_level", 0)
        super().__init__(*args, **kwargs)

    def to_representation(self, instance):
        """Apply proper field filtering based on write_only."""
        representation = super().to_representation(instance)
        if not self._nested:
            return representation

        if not isinstance(self._nested, dict):
            raise DynamicSerializerConfigError("'nested' must be a dictionary")

        for field_name, nested_params in self._nested.items():
            if isinstance(nested_params, dict) and nested_params.get(
                "write_only", False
            ):
                representation.pop(field_name, None)

        return self._apply_dynamic_nested(instance, representation)

    def _apply_dynamic_nested(
        self,
        instance: Any,
        representation: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Process nested serializer configuration ."""
        if not self._nested:
            return representation

        if self._nesting_level >= self.MAX_DEPTH:
            raise ExcessiveNestingError("Depth exceeds safety margin")

        for field_name, original_nested_params in self._nested.items():
            if original_nested_params.get("write_only", False):
                continue

            if not isinstance(original_nested_params, dict):
                raise DynamicSerializerConfigError(
                    f"Nested params for '{field_name}' must be a dictionary"
                )

            nested_params = original_nested_params.copy()

            if not hasattr(instance, field_name):
                continue

            if not isinstance(nested_params, dict):
                raise DynamicSerializerConfigError(
                    f"Nested params for '{field_name}' must be a dictionary"
                )

            if getattr(instance, field_name) is None:
                continue

            try:
                is_many, data_to_serialize = self._prepare_nested_data(
                    instance, field_name, nested_params
                )
            except KeyError as e:
                raise DynamicSerializerConfigError(str(e))

            serializer_class = nested_params.pop("serializer", None)

            if not serializer_class:
                raise DynamicSerializerConfigError(
                    f"Missing serializer for nested field '{field_name}'"
                )

            try:
                serializer = self._build_nested_serializer(
                    serializer_class,
                    data_to_serialize,
                    is_many,
                    nested_params,
                )
                representation[field_name] = serializer.data

            except Exception as e:
                raise DynamicSerializerConfigError(
                    f"Error processing '{field_name}' at level {self._nesting_level}: {str(e)}"
                )

        return representation

    def _prepare_nested_data(self, instance, field_name, nested_params):
        """Prepare data for serialization with clean return-early approach"""

        explicit_instance = nested_params.get("instance")

        if explicit_instance is not None:
            data_to_serialize = (
                explicit_instance(instance, self.context)
                if callable(explicit_instance)
                else explicit_instance
            )
            many = nested_params.get(
                "many",
                isinstance(
                    data_to_serialize, (list, tuple, models.QuerySet, models.Manager)
                ),
            )
            return many, data_to_serialize

        if not hasattr(instance, field_name):
            raise KeyError(f"Field {field_name} not found on instance")

        related_data = getattr(instance, field_name)
        if related_data is None:
            raise KeyError(f"Related data for {field_name} is None")

        data_to_serialize = (
            related_data.all()
            if isinstance(related_data, models.Manager)
            else related_data
        )
        many = nested_params.get(
            "many",
            isinstance(related_data, (models.Manager, models.QuerySet, list, tuple)),
        )

        return many, data_to_serialize

    def _build_nested_serializer(
        self,
        serializer_class,
        data_to_serialize: Any,
        is_many: bool,
        nested_params: Dict[str, Any],
    ):
        """Build serializer with proper parameter handling."""
        params_copy = nested_params.copy()

        next_level_nested = params_copy.pop("nested", None)
        context = self.context.copy()
        context.update(params_copy.pop("context", {}))

        serializer_kwargs = {
            "instance": data_to_serialize,
            "many": is_many,
            "context": context,
            "nested": next_level_nested,
            "nesting_level": self._nesting_level + 1,
        }

        params_copy.pop("instance", None)
        params_copy.pop("many", None)

        common_params = [
            "read_only",
            "write_only",
            "required",
            "default",
            "allow_null",
            "validators",
            "error_messages",
        ]
        for param in common_params:
            if param in params_copy:
                serializer_kwargs[param] = params_copy.pop(param)

        serializer_kwargs.update(params_copy)

        return serializer_class(**serializer_kwargs)

class InlineShapelessSerializerMixin:
    """Inline shapeless serializer mixin that dynamically sets Meta.model and Meta.fields."""

    def __init__(self, *args, **kwargs):
        model = kwargs.pop("model", None)
        if model:
            meta = getattr(self, 'Meta', type('Meta', (), {}))
            meta.model = model
            meta.fields = '__all__'
            self.Meta = meta
        super().__init__(*args, **kwargs)

