Quickstart
==========

This guide will help you get started with Shapeless Serializers quickly.

Basic Setup
-----------

1. Create your shapeless serializer:

.. code-block:: python

   from shapeless_serializers.serializers import ShapelessModelSerializer
   from myapp.models import Book

   class BookSerializer(ShapelessModelSerializer):
       class Meta:
           model = Book
           fields = '__all__'

2. Use dynamic configuration in your view:

.. code-block:: python

   from rest_framework.decorators import api_view
   from rest_framework.response import Response

   @api_view(['GET'])
   def book_detail(request, pk):
       book = Book.objects.get(pk=pk)
       serializer = BookSerializer(
           book,
           fields=['id', 'title', 'author', 'publication_date'],
           rename_fields={'id': 'book_id'}
       )
       return Response(serializer.data)

Common Patterns
---------------

Basic Field Selection
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   serializer = BookSerializer(
       instance,
       fields=['title', 'author', 'price']
   )

Field Renaming
~~~~~~~~~~~~~

.. code-block:: python

   serializer = BookSerializer(
       instance,
       rename_fields={
           'price': 'retail_price',
           'id': 'book_identifier'
       }
   )

Simple Nesting
~~~~~~~~~~~~~

.. code-block:: python

   serializer = BookSerializer(
       instance,
       nested={
           'author': {
               'serializer': AuthorSerializer,
               'fields': ['name', 'bio']
           }
       }
   )

Conditional Fields
~~~~~~~~~~~~~~~~~

.. code-block:: python

   serializer = BookSerializer(
       instance,
       conditional_fields={
           'internal_code': lambda instance, ctx: ctx['request'].user.is_staff
       }
   )

Next Steps
----------

After this quickstart, explore:
- :doc:`features/dynamic_fields` for advanced field selection
- :doc:`features/nested_serializers` for complex relationships
- :doc:`mixins for ultimate customization` for building your own shapeless serializers