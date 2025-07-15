Field Attributes
===============

The Field Attributes feature allows you to dynamically modify serializer field attributes at runtime. This enables you to change field behavior without creating multiple serializer classes.

Basic Usage
-----------

To modify field attributes, pass a ``field_attributes`` dictionary when instantiating your serializer:

.. code-block:: python

   serializer = BlogPostSerializer(
       instance=post,
       field_attributes={
           'title': {'write_only': True},
           'content': {'read_only': False}
       }
   )

Supported Attribute Types
-------------------------

Static Attributes
~~~~~~~~~~~~~~~~

Direct value assignments:

.. code-block:: python

   {
       'title': {'required': True},
       'content': {'help_text': 'Main post content'}
   }

Callable Attributes
~~~~~~~~~~~~~~~~~~

Functions that receive ``(instance, context)`` and return the attribute value:

.. code-block:: python

   def make_write_only(instance, context):
       return not context['request'].user.is_staff

   {
       'secret_field': {'write_only': make_write_only}
   }

Common Attributes
----------------

+-------------------+--------------------------------------------------+-----------------------+
| Attribute         | Description                                      | Example Value         |
+===================+==================================================+=======================+
| ``write_only``    | Field is write-only (excluded from output)       | ``True``/``False``    |
+-------------------+--------------------------------------------------+-----------------------+
| ``read_only``     | Field is read-only (excluded from input)         | ``True``/``False``    |
+-------------------+--------------------------------------------------+-----------------------+
| ``required``      | Whether field is mandatory                       | ``True``/``False``    |
+-------------------+--------------------------------------------------+-----------------------+
| ``help_text``     | Descriptive text for the field                   | ``"User's full name"``|
+-------------------+--------------------------------------------------+-----------------------+
| ``default``       | Default value if field not provided              | ``"draft"``           |
+-------------------+--------------------------------------------------+-----------------------+
| ``allow_null``    | Whether ``None`` is valid value                  | ``True``/``False``    |
+-------------------+--------------------------------------------------+-----------------------+

Examples
----------------

API Versioning
~~~~~~~~~~~~~

Change field behavior between API versions:

.. code-block:: python

   def get_version_attributes(version):
       if version == 'v1':
           return {'legacy_id': {'required': True}}
       return {'uuid': {'required': True}}

   attributes = get_version_attributes(request.version)
   serializer = ResourceSerializer(resource, field_attributes=attributes)


Combining with Other Features
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Field attributes work well with other dynamic features:

.. code-block:: python

   serializer = BlogPostSerializer(
       post,
       fields=['id', 'title', 'content'],
       field_attributes={
           'content': {'write_only': True}
       },
       rename_fields={'id': 'post_id'}
   )


Error Handling
-------------

- Invalid attribute dictionaries raise ``DynamicSerializerConfigError``
- Non-existent fields are silently ignored
- Invalid attribute values raise standard DRF validation errors

See Also
--------

- :doc:`../features/dynamic_fields` - For selecting which fields to include
- :doc:`../features/field_renaming` - For customizing output keys
- :doc:`../features/conditional_fields` - For dynamic field visibility