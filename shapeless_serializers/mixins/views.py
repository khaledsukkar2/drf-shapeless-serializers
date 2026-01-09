from typing import Any, Dict, List, Optional, Set, Union


class ShapelessViewMixin:
    """
    Mixin for DRF Views/ViewSets to automatically inject dynamic configuration
    into ShapelessSerializers.
    """

    def get_serializer(self, *args, **kwargs):
        """
        Override get_serializer to inject dynamic configuration.
        """
        serializer_class = self.get_serializer_class()
        kwargs.setdefault("context", self.get_serializer_context())

        dynamic_config = self.get_serializer_config()

        for key, value in dynamic_config.items():
            if value is not None and key not in kwargs:
                kwargs[key] = value

        return serializer_class(*args, **kwargs)

    def get_serializer_config(self) -> Dict[str, Any]:
        """
        Collects all dynamic configuration parameters.
        Override this if you want full control over the config dict.
        """
        return {
            "fields": self.get_serializer_fields(),
            "nested": self.get_serializer_nested(),
            "rename_fields": self.get_serializer_rename_fields(),
            "field_attributes": self.get_serializer_field_attributes(),
            "conditional_fields": self.get_serializer_conditional_fields(),
        }

    def get_serializer_fields(self) -> Optional[Union[List[str], Set[str]]]:
        """
        Return the list of fields to include.
        Default: Looks for 'serializer_fields' attribute or returns None (all fields).
        """
        return getattr(self, "serializer_fields", None)

    def get_serializer_nested(self) -> Optional[Dict[str, Any]]:
        """
        Return the nested configuration dictionary.
        Default: Looks for 'serializer_nested' attribute or returns None.
        """
        return getattr(self, "serializer_nested", None)

    def get_serializer_rename_fields(self) -> Optional[Dict[str, str]]:
        """
        Return dictionary for renaming fields.
        Default: Looks for 'serializer_rename_fields' attribute or returns None.
        """
        return getattr(self, "serializer_rename_fields", None)

    def get_serializer_field_attributes(self) -> Optional[Dict[str, Dict[str, Any]]]:
        """
        Return dictionary for field attributes.
        Default: Looks for 'serializer_field_attributes' attribute or returns None.
        """
        return getattr(self, "serializer_field_attributes", None)

    def get_serializer_conditional_fields(self) -> Optional[Dict[str, Any]]:
        """
        Return dictionary for conditional fields.
        Default: Looks for 'serializer_conditional_fields' attribute or returns None.
        """
        return getattr(self, "serializer_conditional_fields", None)
