Field Renaming
==============

The Field Renaming feature allows you to dynamically modify field names in your serializer output without changing your models or serializer classes. This is particularly useful for:

- Maintaining backward compatibility in API responses
- Adapting to different client requirements
- Standardizing field names across your API

Basic Usage
-----------

To rename fields, pass a ``rename_fields`` dictionary when instantiating your serializer:

.. code-block:: python

    serializer = BlogPostSerializer(
        instance=post,
        rename_fields={
            'title': 'post_title',
            'id': 'post_id'
        }
    )

Key Features
------------

1. **Simple Renaming**:

   .. code-block:: python

      {
          'old_name': 'new_name'
      }

2. **Multiple Renames**:

   .. code-block:: python

      {
          'title': 'post_title',
          'created_at': 'creation_date',
          'user': 'author'
      }

3. **Nested Field Renaming**:

   .. code-block:: python

      nested={
          'author': {
              'serializer': AuthorSerializer,
              'rename_fields': {
                  'id': 'author_id',
                  'bio': 'biography'
              }
          }
      }

Common Patterns
---------------

API Versioning
~~~~~~~~~~~~~~

Maintain different field names for different API versions:

.. code-block:: python

    def get_field_renaming(version):
        if version == 'v1':
            return {'id': 'post_id'}
        elif version == 'v2':
            return {'id': 'identifier'}
        return {}

    serializer = PostSerializer(
        post,
        rename_fields=get_field_renaming(request.version)
    )

Client-Specific Naming
~~~~~~~~~~~~~~~~~~~~~~

Adapt to different client requirements:

.. code-block:: python

    def get_client_renaming(client_type):
        base_renames = {'id': 'identifier'}
        if client_type == 'ios':
            return {**base_renames, 'title': 'header'}
        elif client_type == 'android':
            return {**base_renames, 'title': 'name'}
        return base_renames

    serializer = PostSerializer(
        post,
        rename_fields=get_client_renaming(request.client_type)
    )

Standardization
~~~~~~~~~~~~~~~

Enforce consistent naming across your API:

.. code-block:: python

    STANDARD_RENAMES = {
        'id': 'identifier',
        'created_at': 'creation_timestamp',
        'updated_at': 'modification_timestamp'
    }

    serializer = PostSerializer(
        post,
        rename_fields=STANDARD_RENAMES
    )

Error Handling
--------------

- Invalid rename configurations raise ``DynamicSerializerConfigError``
- Non-existent fields are silently ignored
- No validation is performed on new field names

.. note::
    The field renaming feature functions as an override for the to_representation method.
    This means that while the field names will appear changed in the output, their names within the serializer itself remain unaltered.
    Therefore, any internal logic or operations involving these fields should refer to their original names, as the renaming only affects the external representation.

See Also
--------

- :doc:`../features/dynamic_fields`
- :doc:`../features/field_attributes`
- :doc:`../features/nested_serializers`