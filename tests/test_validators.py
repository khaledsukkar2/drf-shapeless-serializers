from django.test import TestCase
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from rest_framework.validators import UniqueValidator

from test_app.models import Book, Author
from test_app.serializers import DynamicBookSerializer


class DynamicSerializerTests(TestCase):
    def setUp(self):
        self.author = Author.objects.create(name="Test Author")

    def test_valid_data_passes_validation(self):
        valid_data = {
            "title": "Valid Book",
            "price": 100,
            "author": self.author.id,
            "publication_date": "2023-01-01"
        }
        serializer = DynamicBookSerializer(
            data=valid_data,
            field_validators={
                "price": [MinValueValidator(0)]
            }
        )
        is_valid = serializer.is_valid()
        print(serializer.errors)
        self.assertTrue(is_valid)
        self.assertTrue(serializer.is_valid())

    def test_negative_price_fails_validation(self):
        data = {
            "title": "Bad Book",
            "price": -10,
            "author": self.author.id,
            "publication_date": "2023-01-01"
        }
        serializer = DynamicBookSerializer(
            data=data,
            field_validators={
                "price": [MinValueValidator(0)]
            }
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("price", serializer.errors)

    def test_zero_price_is_valid(self):
        data = {
            "title": "Free Book",
            "price": 0,
            "author": self.author.id,
            "publication_date": "2023-01-01"
        }
        serializer = DynamicBookSerializer(
            data=data,
            field_validators={
                "price": [MinValueValidator(0)]
            }
        )
        self.assertTrue(serializer.is_valid())

    def test_error_message_on_invalid_price(self):
        data = {
            "title": "Invalid",
            "price": -5,
            "author": self.author.id,
            "publication_date": "2023-01-01"
        }
        serializer = DynamicBookSerializer(
            data=data,
            field_validators={
                "price": [MinValueValidator(0)]
            }
        )
        serializer.is_valid()
        self.assertIn("price", serializer.errors)
        self.assertTrue(any("Ensure this value is greater than or equal to 0" in str(msg)
                            for msg in serializer.errors["price"]))

    def test_unique_title_validation(self):
        Book.objects.create(
            title="Existing Title",
            price=10,
            author=self.author,
            publication_date="2022-01-01"
        )

        data = {
            "title": "Existing Title",
            "price": 20,
            "author": self.author.id,
            "publication_date": "2023-01-01"
        }

        serializer = DynamicBookSerializer(
            data=data,
            field_validators={
                "title": [UniqueValidator(queryset=Book.objects.all())]
            }
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("title", serializer.errors)
