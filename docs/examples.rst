Examples
========

This document provides practical examples for all serializer types in the Shapeless Serializers package.

Basic Serializer (ShapelessSerializer)
--------------------------------------

Use this for non-model serialization with full dynamic capabilities.

Example 1: Simple data transformation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from shapeless_serializers.serializers import ShapelessSerializer
    from rest_framework import serializers

    class SurveySerializer(ShapelessSerializer):
        name = serializers.CharField()
        age = serializers.IntegerField()
        email = serializers.EmailField()

    data = {'name': 'John', 'age': 30, 'email': 'john@example.com'}
    serializer = SurveySerializer(
        data=data,
        fields=['name', 'email'],
        rename_fields={'email': 'contact_email'}
    )
    serializer.is_valid()
    print(serializer.data)  # {'name': 'John', 'contact_email': 'john@example.com'}

Example 2: Complex nested structure
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   serializer = SurveySerializer(
       data=data,
       nested={
           'demographics': {
               'serializer': ShapelessSerializer,
               'fields': ['age', 'gender'],
               'nested': {
                   'stats': {
                       'serializer': ShapelessSerializer,
                       'fields': ['score']
                   }
               }
           }
       }
   )

Model Serializer (ShapelessModelSerializer)
-------------------------------------------

The most commonly used serializer for Django models.

Example 1: Basic model serialization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from shapeless_serializers.serializers import ShapelessModelSerializer
   from myapp.models import Product

   class ProductSerializer(ShapelessModelSerializer):
       class Meta:
           model = Product
           fields = '__all__'

   # Usage
   product = Product.objects.get(pk=1)
   serializer = ProductSerializer(
       product,
       fields=['id', 'name', 'price'],
       rename_fields={'price': 'current_price'}
   )

Example 2: Advanced nested relationships
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   serializer = ProductSerializer(
       product,
       fields=['id', 'name', 'supplier', 'categories'],
       nested={
           'supplier': {
               'serializer': SupplierSerializer,
               'fields': ['name', 'contact'],
               'rename_fields': {'contact': 'primary_contact'}
           },
           'categories': {
               'serializer': CategorySerializer,
               'fields': ['name'],
               'many': True
           }
       },
       conditional_fields={
           'internal_code': lambda i,c: c['request'].user.is_staff
       }
   )

Hyperlinked Model Serializer (ShapelessHyperlinkedModelSerializer)
------------------------------------------------------------------

Use this when you need hyperlinked relationships in your API.

Example 1: Basic hyperlinked serialization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from shapeless_serializers.serializers import ShapelessHyperlinkedModelSerializer
   from myapp.models import Book

   class BookSerializer(ShapelessHyperlinkedModelSerializer):
       class Meta:
           model = Book
           fields = ['url', 'title', 'author', 'published_date']

   # Usage
   book = Book.objects.get(pk=1)
   serializer = BookSerializer(
       book,
       context={'request': request},
       fields=['url', 'title', 'author'],
       rename_fields={'url': 'self_link'}
   )

Example 2: Complex hyperlinked relationships
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   serializer = BookSerializer(
       book,
       context={'request': request},
       nested={
           'author': {
               'serializer': AuthorHyperlinkedSerializer,
               'fields': ['url', 'name'],
               'rename_fields': {'url': 'author_link'}
           },
           'publisher': {
               'serializer': PublisherHyperlinkedSerializer,
               'fields': ['url', 'name'],
               'field_attributes': {
                   'url': {'lookup_field': 'uuid'}
               }
           }
       }
   )

API Versioning Pattern
----------------------

.. code-block:: python

   def get_serializer_config(version):
       base_config = {
           'fields': ['id', 'title', 'content'],
           'rename_fields': {'id': f'{version}_id'}
       }
       
       if version == 'v1':
           return {
               **base_config,
               'fields': ['id', 'title', 'excerpt'],
               'rename_fields': {'excerpt': 'summary'}
           }
       elif version == 'v2':
           return {
               **base_config,
               'fields': ['id', 'title', 'content', 'author'],
               'nested': {
                   'author': {
                       'serializer': AuthorSerializer,
                       'fields': ['name']
                   }
               }
           }
       return base_config

   # Usage
   post = Post.objects.get(pk=1)
   config = get_serializer_config(request.version)
   serializer = PostSerializer(post, **config)

See Also
--------

* :doc:`features/dynamic_fields`
* :doc:`features/field_attributes` 
* :doc:`features/custom_serializers`