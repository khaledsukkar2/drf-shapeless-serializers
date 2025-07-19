Inline Shapeless Model Serializers
========================

The ``InlineShapelessModelSerializer`` allows you to create serializers on-the-fly without defining a serializer class. This is particularly useful for one-off serialization needs or when you need to dynamically create serializers based on runtime conditions.

Basic Usage
----------

To use the ``InlineShapelessModelSerializer``, you need to provide a model parameter:

.. code-block:: python

    from shapeless_serializers.serializers import InlineShapelessModelSerializer
    from myapp.models import Author

    # Get an author instance
    author = Author.objects.get(pk=1)

    # Create an inline serializer with a model
    serializer = InlineShapelessModelSerializer(author, model=Author)
    serializer.data  # Contains all fields from the Author model


Limiting Fields
--------------

You can limit the fields included in the serialized output:

.. code-block:: python

    serializer = InlineShapelessModelSerializer(
        author, 
        model=Author, 
        fields=['name', 'bio']
    )
    serializer.data  # Contains only 'name' and 'bio' fields


Nested Relationships
------------------

You can include related models in the serialized output:

.. code-block:: python

    from myapp.models import Book

    book = Book.objects.get(pk=1)

    serializer = InlineShapelessModelSerializer(
        book,
        model=Book,
        fields=['title', 'author', 'price'],
        nested={
            'author': {
                'serializer': InlineShapelessModelSerializer,
                'model': Author,
                'fields': ['name', 'bio']
            }
        }
    )
    serializer.data  # Contains 'title', 'price', and nested 'author' with 'name' and 'bio'


Field Renaming
------------

You can rename fields in the serialized output:

.. code-block:: python

    serializer = InlineShapelessModelSerializer(
        author,
        model=Author,
        rename_fields={'name': 'author_name', 'bio': 'biography'}
    )
    serializer.data  # Contains 'author_name' and 'biography' instead of 'name' and 'bio'


Conditional Fields
---------------

You can conditionally include or exclude fields based on conditions:

.. code-block:: python

    # Only include bio if show_bio is True
    show_bio = request.query_params.get('show_bio', '').lower() == 'true'

    serializer = InlineShapelessModelSerializer(
        author,
        model=Author,
        conditional_fields={
            'bio': show_bio
        }
    )
    serializer.data  # Contains 'bio' only if show_bio is True


Field Attributes
--------------

You can modify field attributes dynamically:

.. code-block:: python

    serializer = InlineShapelessModelSerializer(
        book,
        model=Book,
        field_attributes={
            'title': {'read_only': True},  # Make title read-only
            'price': {'label': 'Retail Price', 'help_text': 'Price in USD'}
        }
    )


Multiple Instances
---------------

You can serialize multiple instances by setting ``many=True``:

.. code-block:: python

    authors = Author.objects.all()

    serializer = InlineShapelessModelSerializer(
        authors,
        model=Author,
        many=True,
        fields=['id', 'name']
    )
    serializer.data  # Contains a list of authors with 'id' and 'name' fields


Complex Example
-------------

You can combine multiple features for complex serialization needs:

.. code-block:: python

    from myapp.models import BlogPost, AuthorProfile, Tag, Category, User

    post = BlogPost.objects.get(pk=1)

    serializer = InlineShapelessModelSerializer(
        post,
        model=BlogPost,
        fields=['title', 'content', 'author', 'tags', 'categories'],
        nested={
            'author': {
                'serializer': InlineShapelessModelSerializer,
                'model': AuthorProfile,
                'fields': ['bio', 'user'],
                'nested': {
                    'user': {
                        'serializer': InlineShapelessModelSerializer,
                        'model': User,
                        'fields': ['username', 'email']
                    }
                }
            },
            'tags': {
                'serializer': InlineShapelessModelSerializer,
                'model': Tag,
                'fields': ['name'],
                'many': True
            },
            'categories': {
                'serializer': InlineShapelessModelSerializer,
                'model': Category,
                'fields': ['name'],
                'many': True
            }
        },
        rename_fields={'title': 'post_title'}
    )