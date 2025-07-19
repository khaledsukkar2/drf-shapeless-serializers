from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Book, Author

from .serializers import (
    DynamicBookSerializer,
    DynamicAuthorSerializer,
    UserSerializer)

from shapeless_serializers.serializers import InlineDynamicModelSerializer

from rest_framework.validators import (
    UniqueValidator,
)
from django.core.validators import MinValueValidator



@api_view(['GET'])
def book_detail(request, pk):
    book = Book.objects.get(pk=pk)

    serializer = DynamicBookSerializer(
        book,
        fields=['id', 'title', 'price', 'author'],
        rename_fields={'price': 'retail_price', 'id': 'book_id'},
        nested={
            'author': {
                'serializer': DynamicAuthorSerializer,
                'fields': ['id', 'bio', 'user'],
                'rename_fields': {'bio': 'biography'},
                'nested': {
                    'user': {
                        'serializer': UserSerializer,
                        'fields': ['id', 'username', 'email']
                    }
                }
            }
        }
    )

    return Response(serializer.data)

@api_view(['POST'])
def create_book(request):
    field_validators = {
        "title": [UniqueValidator(queryset=Book.objects.all())],
        "price": [MinValueValidator(0)]
    }

    serializer = DynamicBookSerializer(
        data=request.data,
        fields=['title', 'price'],
        field_validators=field_validators
    )

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)


# Examples of InlineDynamicModelSerializer usage

@api_view(['GET'])
def author_detail_inline(request, pk):
    """
    Example of using InlineDynamicModelSerializer with basic model parameter.
    This demonstrates how to create a serializer on-the-fly without defining a serializer class.
    """
    author = Author.objects.get(pk=pk)
    
    # Create an inline serializer with a model
    serializer = InlineDynamicModelSerializer(author, model=Author)
    
    return Response(serializer.data)


@api_view(['GET'])
def book_detail_inline(request, pk):
    """
    Example of using InlineDynamicModelSerializer with fields parameter.
    This demonstrates how to limit the fields in the serialized output.
    """
    book = Book.objects.get(pk=pk)
    
    # Create an inline serializer with a model and fields
    serializer = InlineDynamicModelSerializer(
        book, 
        model=Book, 
        fields=['title', 'price']
    )
    
    return Response(serializer.data)
