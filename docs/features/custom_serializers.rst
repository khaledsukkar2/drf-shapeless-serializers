Creating Custom Shapeless Serializers
=====================================

For developers who need only specific features, you can create your own serializer combinations by mixing individual components.

Why Build Custom Serializers?
-----------------------------

- Reduce overhead by including only what you need
- Create specialized serializers for different parts of your application
- Maintain finer control over serializer behavior

Available Mixins
----------------

+-----------------------------------+---------------------------------------------------------------+
| Mixin                             | Description                                                   |
+===================================+===============================================================+
| ``DynamicFieldsMixin``            | Select which fields to include at runtime                     |
+-----------------------------------+---------------------------------------------------------------+
| ``DynamicFieldAttributesMixin``   | Modify field attributes (read_only, write_only, etc.)         |
+-----------------------------------+---------------------------------------------------------------+
| ``DynamicFieldRenamingMixin``     | Rename output fields without changing models                  |
+-----------------------------------+---------------------------------------------------------------+
| ``DynamicNestedSerializerMixin``  | Configure nested relationships dynamically                    |
+-----------------------------------+---------------------------------------------------------------+
| ``DynamicConditionalFieldsMixin`` | Include/exclude fields based on conditions                    |
+-----------------------------------+---------------------------------------------------------------+

Basic Custom Serializer Examples
--------------------------------

Field Selection Only
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from rest_framework import serializers
    from shapeless_serializers.mixins import DynamicFieldsMixin

    class LightweightSerializer(DynamicFieldsMixin, serializers.Serializer):
        """Only includes dynamic field selection"""
        pass

Field Selection + Renaming
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from rest_framework import serializers
    from shapeless_serializers.mixins import (
        DynamicFieldsMixin,
        DynamicFieldRenamingMixin
    )

    class ReportingSerializer(DynamicFieldsMixin, 
                            DynamicFieldRenamingMixin,
                            serializers.ModelSerializer):
        """For external reporting with custom field names"""
        pass

Nested Relationships Only
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from rest_framework import serializers
    from shapeless_serializers.mixins import DynamicNestedSerializerMixin

    class NestedOnlySerializer(DynamicNestedSerializerMixin,
                              serializers.ModelSerializer):
        """Just handles dynamic nested relationships"""
        pass

See Also
--------

- :doc:`../features/dynamic_fields`
- :doc:`../features/field_attributes` 
- :doc:`../features/nested_serializers`