ShapelessViewMixin
==================

The ``ShapelessViewMixin`` allows you to integrate dynamic serializer configuration seamlessly into your Django REST Framework Views and ViewSets.

Instead of instantiating serializers manually with dynamic configuration, you can define the configuration on the View itself, and the mixin will automatically inject it when ``get_serializer`` is called.

Basic Usage
-----------

Inherit from ``ShapelessViewMixin`` in your ViewSet or GenericAPIView:

.. code-block:: python

    from rest_framework import viewsets
    from shapeless_serializers.mixins.views import ShapelessViewMixin
    from .models import BlogPost
    from .serializers import DynamicBlogPostSerializer, DynamicAuthorProfileSerializer

    class BlogPostViewSet(ShapelessViewMixin, viewsets.ModelViewSet):
        queryset = BlogPost.objects.all()
        serializer_class = DynamicBlogPostSerializer

        # Dynamic configuration
        serializer_fields = ["id", "title", "author"]
        serializer_nested = {
            "author": DynamicAuthorProfileSerializer(fields=["user", "bio"])
        }

Configuration Methods
---------------------

You can override methods to provide dynamic configuration based on the request (e.g., action, user permissions).

.. code-block:: python

    class BlogPostViewSet(ShapelessViewMixin, viewsets.ModelViewSet):
        # ...

        def get_serializer_fields(self):
            if self.action == 'list':
                return ["id", "title", "author"]
            return ["id", "title", "content", "author", "comments"]

        def get_serializer_nested(self):
            if self.action == 'retrieve':
                return {
                    "comments": DynamicCommentSerializer(many=True)
                }
            return {}

Available Configuration Hooks
-----------------------------

- ``get_serializer_fields()``: Returns list of fields.
- ``get_serializer_nested()``: Returns nested configuration dict.
- ``get_serializer_rename_fields()``: Returns rename mapping dict.
- ``get_serializer_field_attributes()``: Returns field attributes dict.
- ``get_serializer_conditional_fields()``: Returns conditional fields dict.
