Conditional Fields
==================

The Conditional Fields feature allows you to dynamically include or exclude fields based on runtime conditions. This is particularly useful for:

- Role-based field visibility (admin vs regular users)
- Context-specific data presentation
- Preventing sensitive data leakage
- API versioning or feature flags

Basic Usage
-----------

To conditionally include fields, pass a ``conditional_fields`` dictionary when instantiating your serializer:

.. code-block:: python

    serializer = BlogPostSerializer(
        instance=post,
        conditional_fields={
            'view_count': lambda instance, ctx: ctx['request'].user.is_staff,
            'draft_content': False  # Always exclude
        }
    )

The parameters for the condition function are:

- ``instance``: Provides full access to the current instance
- ``context``: Allows adding custom context for any condition

You can use either a ``lambda`` expression or pass the function with the required parameters directly:

.. code-block:: python

    serializer1 = CommentSerializer(
        instance=comment,
        context={"request": request},
        conditional_fields={"content": owner_only},  # Function reference
    )

Condition Types
---------------

Boolean Conditions
~~~~~~~~~~~~~~~~~~

Simple True/False values for unconditional inclusion/exclusion:

.. code-block:: python

    {
        'public_field': True,    # Always include
        'private_field': False   # Always exclude
    }

Callable Conditions
~~~~~~~~~~~~~~~~~~~

Functions that receive ``(instance, context)`` and return boolean:

.. code-block:: python

    def is_admin(instance, context):
        return context['request'].user.is_staff

    {
        'admin_only_field': is_admin,
        'owner_field': lambda i, c: i.owner == c['request'].user
    }

Common Patterns
---------------

Role-Based Access
~~~~~~~~~~~~~~~~~

Show different fields to different user roles:

.. code-block:: python

    def get_role_conditions(user):
        return {
            'internal_id': user.is_staff,
            'metrics': user.is_staff,
            'draft_content': user.has_perm('edit_content'),
            'author_notes': lambda i, c: i.author == c['request'].user
        }

    conditions = get_role_conditions(request.user)
    serializer = PostSerializer(post, conditional_fields=conditions)

Context-Sensitive Fields
~~~~~~~~~~~~~~~~~~~~~~~~

Adjust fields based on request context:

.. code-block:: python

    serializer = UserSerializer(
        user,
        conditional_fields={
            'email': lambda i, c: c['show_email'],
            'phone': lambda i, c: c['request'].query_params.get('show_contact')
        },
        context={'show_email': True, 'request': request}
    )

Feature Flags
~~~~~~~~~~~~~

Enable fields based on feature flags:

.. code-block:: python

    from features import is_enabled

    serializer = ProductSerializer(
        product,
        conditional_fields={
            'experimental_feature': lambda i, c: is_enabled('experimental_ui')
        }
    )

More Examples
-------------

Context-Dependent Conditions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Different output for staff vs regular users:

.. code-block:: python

    serializer = BlogPostSerializer(
        post,
        context={'request': request},
        conditional_fields={
            'view_count': lambda i, c: c['request'].user.is_staff
        }
    )

Complex Conditions
~~~~~~~~~~~~~~~~~~

Multiple context checks:

.. code-block:: python

    def should_show_field(instance, context):
        return (
            context['request'].user.is_authenticated and
            context['show_details'] and
            instance.status == 'published'
        )

    serializer = BlogPostSerializer(
        post,
        context={'request': request, 'show_details': True},
        conditional_fields={'content': should_show_field}
    )

Nested Conditional Fields
-------------------------

Apply conditions to nested serializers:

.. code-block:: python

    serializer = BlogPostSerializer(
        post,
        nested={
            'author': {
                'serializer': AuthorSerializer,
                'conditional_fields': {
                    'email': lambda i, c: c['request'].user.is_staff
                }
            }
        }
    )

Error Handling
--------------

The system handles several error cases gracefully:

- Invalid conditions raise ``DynamicSerializerConfigError``
- Non-existent fields are silently ignored
- Failed condition evaluations provide detailed error messages

.. note::
    If the passed value for the condition is not callable, then ``bool()`` will be applied to it and return True/False based on the result.

See Also
--------

- :doc:`../features/dynamic_fields` - For basic field selection
- :doc:`../features/nested_serializers` - For conditional nested relationships