from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Book

from .serializers import (
    DynamicBookSerializer,
    DynamicAuthorSerializer,
    UserSerializer)

from rest_framework.validators import (
    UniqueValidator,
    UniqueTogetherValidator
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
        "price": [MinValueValidator(0)],
    }

    meta_validators = [
        UniqueTogetherValidator(
            queryset=Book.objects.all(),
            fields=["title", "author"]
        )
    ]

    serializer = DynamicBookSerializer(
        data=request.data,
        fields=["title", "price", "author"],
        field_validators=field_validators,
        meta_validators=meta_validators
    )

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
