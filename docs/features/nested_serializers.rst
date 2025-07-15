Nested Serializers
=================

The Nested Serializers feature provides powerful, dynamic control over related object serialization. It allows you to configure nested relationships at runtime with full control over each level's behavior.

Basic Usage
-----------

Configure nested relationships using the ``nested`` parameter:

.. code-block:: python

   serializer = BlogPostSerializer(
       instance=post,
       nested={
           'author': {
               'serializer': AuthorSerializer,
               'fields': ['name', 'bio']
           }
       }
   )

Nested Configuration Options
----------------------------

+-------------------+--------------------------------------------------+--------------------------------+
| Option            | Description                                      | Example                        |
+===================+==================================================+================================+
| ``serializer``    | Serializer class to use for the relationship     | ``AuthorSerializer``           |
+-------------------+--------------------------------------------------+--------------------------------+
| ``fields``        | Fields to include from nested serializer        | ``['id', 'name']``             |
+-------------------+--------------------------------------------------+--------------------------------+
| ``rename_fields`` | Field name mappings for output                  | ``{'id': 'author_id'}``        |
+-------------------+--------------------------------------------------+--------------------------------+
| ``field_attrs``   | Dynamic field attributes                        | ``{'bio': {'write_only': True}}``|
+-------------------+--------------------------------------------------+--------------------------------+
| ``conditional``   | Conditional field inclusion                     | ``{'email': lambda i,c: ...}`` |
+-------------------+--------------------------------------------------+--------------------------------+
| ``nested``        | Further nested relationships                   | (see deep nesting example)     |
+-------------------+--------------------------------------------------+--------------------------------+
| ``many``          | For many-to-many relationships (default: auto)  | ``True``/``False``             |
+-------------------+--------------------------------------------------+--------------------------------+
| ``instance``      | Custom queryset/instance for the relationship   | ``post.comments.filter(...)``  |
+-------------------+--------------------------------------------------+--------------------------------+

.. note::
    please note that:To enable features such as field renaming and dynamic fields, nested serializers must inherit from either shapeless serializers or appropriate mixins.

Deep Nesting
------------

Create arbitrarily deep nested structures:

.. code-block:: python

   serializer = BlogPostSerializer(
       post,
       nested={
           'author': {
               'serializer': AuthorSerializer,
               'nested': {
                   'user': {
                       'serializer': UserSerializer,
                       'nested': {
                           'profile': {
                               'serializer': ProfileSerializer
                           }
                       }
                   }
               }
           }
       }
   )

The system automatically prevents circular references.


Examples
---------------

Selective Field Inclusion
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Only include specific fields from nested objects
   nested={
       'author': {
           'serializer': AuthorSerializer,
           'fields': ['name', 'bio']
       }
   }


The system handles even the most complex and deeply nested relationships with ease

Example With Complex Relationships
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

  serializer = DynamicBlogPostSerializer(
           posts,
            fields=["id", "title", "author", "comments"],
            rename_fields={"id": "post_identifier"},
            nested={
                "author": {
                    "serializer": DynamicAuthorProfileSerializer,
                    "fields": ["bio", "is_verified", 'user'],
                    "rename_fields": {"bio": "author_biography"},
                    "field_attributes": {
                        "is_verified": {"help_text": "Verified status"}
                    },
                    "nested": {
                        "user": {
                            "serializer": UserSerializer,
                            "fields": ["id", "username"],
                            "rename_fields": {"username": "user_login"},
                        }
                    },
                },
                "comments": {
                    "serializer": DynamicCommentSerializer,
                    "fields": ["id", "content", "user", "replies"],
                    "instance": posts.comments.filter(
                        is_approved=True, parent__isnull=True
                    ),
                    "rename_fields": {"content": "comment_text"},
                    "field_attributes": {"id": {"label": "Comment ID"}},
                    "nested": {
                        "user": {
                            "serializer": UserSerializer,
                            "fields": ["id", "username"],
                            "rename_fields": {"username": "commenter_name"},
                        },
                        "replies": {
                            "serializer": DynamicCommentSerializer,
                            "fields": ["id", "content", "user"],
                            "instance": lambda instance, ctx: instance.replies.filter(is_approved=True)
                            "rename_fields": {"content": "reply_text"},
                            "field_attributes": {"id": {"label": "Reply ID"}},
                            "nested": {
                                "user": {
                                    "serializer": UserSerializer,
                                    "fields": ["id", "username"],
                                    "rename_fields": {"username": "replier_name"},
                                }

                            },

                        },

                    },

                },

            },

        )

Example with very deep relationships
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   serializer = DynamicBlogPostSerializer(
            posts,
            fields=["id", "title", "author", "tags", "comments", "likes"],
            nested={
                "author": {
                    "serializer": DynamicAuthorProfileSerializer,
                    "fields": ["id", "bio", "user"],
                    "nested": {
                        "user": {
                            "serializer": UserSerializer,
                            "fields": [
                                "id",
                                "email",
                            ],
                            "nested": {
                                "author_profile": {
                                    "serializer": DynamicAuthorProfileSerializer,
                                    "fields": ["bio"],
                                    "nested": {
                                        "blog_posts": {
                                            "serializer":DynamicBlogPostSerializer,
                                            "fields": ["title"],
                                            "nested": {
                                                "tags": {
                                                    "serializer": TagSerializer,
                                                    "fields": ["name"],
                                                    "many":True,
                                                }

                                            },

                                        }

                                    },

                                }

                            },

                        }

                    },
                    },

                },
             )



Error Handling
-------------

- Invalid configurations raise ``DynamicSerializerConfigError``
- Missing serializers raise clear error messages
- Circular references are automatically prevented

See Also
--------

- :doc:`../features/dynamic_fields` - For controlling top-level fields
- :doc:`../features/field_attributes` - For modifying nested field behavior
- :doc:`../features/custom_serializers.rst` - For creating custom dynamic serializers