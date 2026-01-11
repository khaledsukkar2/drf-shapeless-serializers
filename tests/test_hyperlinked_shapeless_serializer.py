from django.test import TestCase, override_settings
from django.urls import path
from rest_framework.response import Response
from rest_framework.test import APIRequestFactory
from rest_framework.views import APIView

from shapeless_serializers.serializers import ShapelessHyperlinkedModelSerializer
from test_app.models import Author, Book

# --- Setup for URL resolution ---


class MockView(APIView):
    """A dummy view to handle the detail URL resolution."""

    def get(self, request, pk=None):
        return Response({"status": "ok"})


# Define URL patterns at module level so Django can find them
urlpatterns = [
    path("authors/<int:pk>/", MockView.as_view(), name="author-detail"),
    path("books/<int:pk>/", MockView.as_view(), name="book-detail"),
]

# --- Serializers ---


class AuthorHyperlinkedSerializer(ShapelessHyperlinkedModelSerializer):
    class Meta:
        model = Author
        fields = ["url", "name", "bio"]
        # Explicitly map the URL field to the view name defined above
        extra_kwargs = {"url": {"view_name": "author-detail", "lookup_field": "pk"}}


class BookHyperlinkedSerializer(ShapelessHyperlinkedModelSerializer):
    class Meta:
        model = Book
        fields = ["url", "title", "author"]
        # Explicitly map the URL field to the view name defined above
        extra_kwargs = {"url": {"view_name": "book-detail", "lookup_field": "pk"}}


# --- Tests ---


@override_settings(ROOT_URLCONF=__name__)
class ShapelessHyperlinkedSerializerTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        # Ensure the request has a host header so full URLs (http://testserver/...) can be generated
        self.request = self.factory.get("/", HTTP_HOST="testserver")

        self.author = Author.objects.create(name="Jane Doe", bio="Writer")
        self.book = Book.objects.create(
            title="Jane's Journey",
            author=self.author,
            price=10.00,
            publication_date="2023-01-01",
        )

    def test_basic_hyperlink_generation(self):
        """Test that the URL field is generated correctly."""
        serializer = AuthorHyperlinkedSerializer(
            instance=self.author, context={"request": self.request}
        )
        data = serializer.data
        self.assertIn("url", data)
        # Verify the URL structure matches our pattern
        self.assertIn(f"/authors/{self.author.id}/", data["url"])
        self.assertEqual(data["name"], "Jane Doe")

    def test_dynamic_fields_on_hyperlinked_serializer(self):
        """Test limiting fields, including the URL field."""
        # 1. Include URL explicitly
        serializer = AuthorHyperlinkedSerializer(
            instance=self.author,
            fields=["url", "name"],
            context={"request": self.request},
        )
        data = serializer.data
        self.assertIn("url", data)
        self.assertNotIn("bio", data)

        # 2. Exclude URL explicitly via fields list
        serializer_no_url = AuthorHyperlinkedSerializer(
            instance=self.author, fields=["name"], context={"request": self.request}
        )
        data_no_url = serializer_no_url.data
        self.assertNotIn("url", data_no_url)

    def test_nested_hyperlinked_serializers(self):
        """Test nesting one hyperlinked serializer inside another."""
        serializer = BookHyperlinkedSerializer(
            instance=self.book,
            fields=["title", "author"],
            context={"request": self.request},
            nested={
                "author": AuthorHyperlinkedSerializer(
                    fields=["url", "name"], rename_fields={"name": "author_name"}
                )
            },
        )

        data = serializer.data
        self.assertEqual(data["title"], "Jane's Journey")

        # Check nested data
        author_data = data["author"]
        self.assertIn("url", author_data)
        self.assertIn(f"/authors/{self.author.id}/", author_data["url"])
        self.assertIn("author_name", author_data)
        self.assertEqual(author_data["author_name"], "Jane Doe")

    def test_conditional_url_inclusion(self):
        """Test conditionally showing the URL field."""

        # Condition: Show URL only if 'show_links' is in context
        def show_url_condition(instance, context):
            return context.get("show_links", False)

        # Case 1: Hide URL
        serializer_hidden = AuthorHyperlinkedSerializer(
            instance=self.author,
            context={"request": self.request, "show_links": False},
            conditional_fields={"url": show_url_condition},
        )
        self.assertNotIn("url", serializer_hidden.data)

        # Case 2: Show URL
        serializer_shown = AuthorHyperlinkedSerializer(
            instance=self.author,
            context={"request": self.request, "show_links": True},
            conditional_fields={"url": show_url_condition},
        )
        self.assertIn("url", serializer_shown.data)

    def test_renaming_hyperlink_field(self):
        """Test renaming the 'url' field to something else (e.g., 'self_link')."""
        serializer = AuthorHyperlinkedSerializer(
            instance=self.author,
            rename_fields={"url": "self_link"},
            context={"request": self.request},
        )
        data = serializer.data
        self.assertIn("self_link", data)
        self.assertNotIn("url", data)
        self.assertIn(f"/authors/{self.author.id}/", data["self_link"])
