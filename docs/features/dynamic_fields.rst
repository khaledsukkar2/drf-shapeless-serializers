Dynamic Fields
==============

The Dynamic Fields feature allows you to select which fields should be included in your serializer input/output at runtime. This provides flexibility to create different views of your data without creating multiple serializer classes.

Basic Usage
-----------

To specify which fields to include, pass a ``fields`` parameter when instantiating your serializer:

.. code-block:: python

    serializer = AuthorProfileSerializer(
        instance=author,
        fields=['bio', 'website']
    )

This will only include the ``bio`` and ``website`` fields in the output.

Field Selection Types
---------------------

List of Fields
~~~~~~~~~~~~~~

.. code-block:: python

    fields=['id', 'title', 'created_at']

Tuple of Fields
~~~~~~~~~~~~~~~

.. code-block:: python

    fields=('id', 'title', 'status')

Set of Fields
~~~~~~~~~~~~~

.. code-block:: python

    fields={'username', 'email', 'last_login'}

Behavior Notes
--------------

- Non-existent fields are silently ignored
- Write-only fields are never included in output (even if specified)
- The field selection applies to both top-level and nested serializers

Common Patterns
---------------

API Versioning
~~~~~~~~~~~~~~

Show different fields for different API versions:

.. code-block:: python

    def get_serializer_fields(version):
        if version == 'v1':
            return ['id', 'title', 'content']
        elif version == 'v2':
            return ['id', 'title', 'excerpt', 'author']
        return '__all__'

    fields = get_serializer_fields(request.version)
    serializer = PostSerializer(post, fields=fields)

Client-Specific Views
~~~~~~~~~~~~~~~~~~~~~

Customize output for different client types:

.. code-block:: python

    def get_client_fields(client_type):
        base_fields = ['id', 'title']
        if client_type == 'mobile':
            return base_fields + ['excerpt']
        elif client_type == 'web':
            return base_fields + ['content', 'related_posts']
        return base_fields

    fields = get_client_fields(request.client_type)
    serializer = PostSerializer(post, fields=fields)

Nested Field Control
--------------------

Control fields for nested relationships:

.. code-block:: python

    serializer = BlogPostSerializer(
        instance=post,
        fields=['id', 'title', 'author'],
        nested={
            'author': {
                'serializer': AuthorSerializer,
                'fields': ['name', 'avatar']
            }
        }
    )

Examples
--------

Combining with Other Features
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Dynamic fields work well with other serializer features:

.. code-block:: python

    serializer = BlogPostSerializer(
        post,
        fields=['id', 'title', 'author'],
        rename_fields={'id': 'post_id'},
        conditional_fields={
            'stats': lambda i, c: c['request'].user.is_staff
        }
    )

Field Presets
~~~~~~~~~~~~~

Create reusable field configurations:

.. code-block:: python

    POST_FIELD_PRESETS = {
        'list': ['id', 'title', 'excerpt'],
        'detail': ['id', 'title', 'content', 'author', 'categories'],
        'admin': '__all__'
    }

    # Usage
    serializer = PostSerializer(
        post,
        fields=POST_FIELD_PRESETS['detail']
    )

Error Handling
--------------

- Invalid field containers (e.g., strings instead of lists) raise ``DynamicSerializerConfigError``
- The serializer will ignore:
  - Non-existent fields
  - Write-only fields (even if requested)

See Also
--------

- :doc:`../features/field_attributes` - For modifying field behavior
- :doc:`../features/field_renaming` - For customizing output keys
- :doc:`../features/conditional_fields` - For dynamic field visibility