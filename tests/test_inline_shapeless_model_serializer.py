from django.contrib.auth import get_user_model
from django.test import TestCase

from shapeless_serializers.exceptions import DynamicSerializerConfigError
from shapeless_serializers.serializers import InlineShapelessModelSerializer
from test_app.models import Author, AuthorProfile, BlogPost, Book, Category, Tag

User = get_user_model()


class InlineShapelessModelSerializerTests(TestCase):
    """Tests for the InlineShapelessModelSerializer class using the new instance-based nesting."""

    def setUp(self):
        # Create test users
        self.user1 = User.objects.create(username="user1", email="user1@example.com")

        # Create test authors
        self.author1 = Author.objects.create(name="Test Author", bio="Author biography")

        # Create test books
        self.book1 = Book.objects.create(
            title="Test Book",
            author=self.author1,
            price=29.99,
            publication_date="2023-01-01",
        )

        # Create author profile
        self.author_profile = AuthorProfile.objects.create(
            user=self.user1, bio="Author bio", website="https://author.com"
        )

        # Create blog post
        self.post = BlogPost.objects.create(
            title="Test Post",
            slug="test-post",
            author=self.author_profile,
            content="Test content",
        )

        # Create tags and categories
        self.tag1 = Tag.objects.create(name="Django", slug="django")
        self.category1 = Category.objects.create(name="Technology", slug="tech")

        self.post.tags.add(self.tag1)
        self.post.categories.add(self.category1)

    def test_inline_serializer_with_model(self):
        """Test that InlineShapelessModelSerializer correctly sets model and fields."""
        # Create an inline serializer with a model
        serializer = InlineShapelessModelSerializer(self.author1, model=Author)

        # Check that the serializer has the correct model and fields
        self.assertEqual(serializer.Meta.model, Author)
        self.assertEqual(serializer.Meta.fields, "__all__")

        # Check that the serializer data contains the expected fields
        data = serializer.data
        self.assertIn("name", data)
        self.assertIn("bio", data)
        self.assertEqual(data["name"], "Test Author")
        self.assertEqual(data["bio"], "Author biography")

    def test_inline_serializer_with_fields(self):
        """Test that InlineShapelessModelSerializer works with fields parameter."""
        # Create an inline serializer with a model and fields
        serializer = InlineShapelessModelSerializer(
            self.book1, model=Book, fields=["title", "price"]
        )

        # Check that the serializer data contains only the specified fields
        data = serializer.data
        self.assertIn("title", data)
        self.assertIn("price", data)
        self.assertNotIn("publication_date", data)
        self.assertEqual(data["title"], "Test Book")
        self.assertEqual(float(data["price"]), 29.99)

    def test_inline_serializer_with_nested(self):
        """Test that InlineShapelessModelSerializer works with nested instances."""
        # Create an inline serializer with nested relationships using the new instance pattern
        serializer = InlineShapelessModelSerializer(
            self.book1,
            model=Book,
            fields=["title", "author"],
            nested={
                # Instantiate the nested serializer directly
                "author": InlineShapelessModelSerializer(model=Author, fields=["name"])
            },
        )

        # Check that the serializer data contains the nested relationship
        data = serializer.data
        self.assertIn("author", data)
        self.assertIn("name", data["author"])
        self.assertEqual(data["author"]["name"], "Test Author")

    def test_inline_serializer_with_field_attributes(self):
        """Test that InlineShapelessModelSerializer works with field_attributes parameter."""
        # Create an inline serializer with field attributes
        serializer = InlineShapelessModelSerializer(
            self.author1,
            model=Author,
            field_attributes={"name": {"read_only": True}, "bio": {"required": False}},
        )

        # Check that the field attributes were applied
        self.assertTrue(serializer.fields["name"].read_only)
        self.assertFalse(serializer.fields["bio"].required)

    def test_inline_serializer_with_rename_fields(self):
        """Test that InlineShapelessModelSerializer works with rename_fields parameter."""
        # Create an inline serializer with renamed fields
        serializer = InlineShapelessModelSerializer(
            self.author1,
            model=Author,
            rename_fields={"name": "author_name", "bio": "biography"},
        )

        # Check that the fields were renamed in the output
        data = serializer.data
        self.assertIn("author_name", data)
        self.assertIn("biography", data)
        self.assertNotIn("name", data)
        self.assertNotIn("bio", data)
        self.assertEqual(data["author_name"], "Test Author")
        self.assertEqual(data["biography"], "Author biography")

    def test_inline_serializer_with_conditional_fields(self):
        """Test that InlineShapelessModelSerializer works with conditional_fields parameter."""
        # Create an inline serializer with conditional fields
        serializer = InlineShapelessModelSerializer(
            self.author1,
            model=Author,
            conditional_fields={"bio": False},  # Exclude bio field
        )

        # Check that the conditional fields were applied
        data = serializer.data
        self.assertIn("name", data)
        self.assertNotIn("bio", data)

    def test_inline_serializer_without_model(self):
        """Test that InlineShapelessModelSerializer works without model parameter (subclassing)."""

        # Create a subclass with Meta class
        class AuthorInlineSerializer(InlineShapelessModelSerializer):
            class Meta:
                model = Author
                fields = ["name"]

        # Create an instance of the serializer
        serializer = AuthorInlineSerializer(self.author1)

        # Check that the serializer data contains the expected fields
        data = serializer.data
        self.assertIn("name", data)
        self.assertNotIn("bio", data)
        self.assertEqual(data["name"], "Test Author")

    def test_inline_serializer_many_true(self):
        """Test that InlineShapelessModelSerializer works with many=True."""
        # Create multiple authors
        author2 = Author.objects.create(name="Second Author", bio="Another biography")
        authors = [self.author1, author2]

        # Create an inline serializer with many=True
        serializer = InlineShapelessModelSerializer(
            authors, model=Author, many=True, fields=["name"]
        )

        # Check that the serializer data contains multiple items
        data = serializer.data
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["name"], "Test Author")
        self.assertEqual(data[1]["name"], "Second Author")

    def test_inline_serializer_complex_case(self):
        """Test a complex case with deep nesting using serializer instances."""
        # Create an inline serializer with multiple features
        serializer = InlineShapelessModelSerializer(
            self.post,
            model=BlogPost,
            fields=["title", "content", "author", "tags", "categories"],
            rename_fields={"title": "post_title"},
            nested={
                # Nested Level 1: Author Profile
                "author": InlineShapelessModelSerializer(
                    model=AuthorProfile,
                    fields=["bio", "user"],
                    nested={
                        # Nested Level 2: User
                        "user": InlineShapelessModelSerializer(
                            model=User, fields=["username", "email"]
                        )
                    },
                ),
                # Nested Many Relationships
                "tags": InlineShapelessModelSerializer(
                    model=Tag, fields=["name"], many=True
                ),
                "categories": InlineShapelessModelSerializer(
                    model=Category, fields=["name"], many=True
                ),
            },
        )

        # Check the complex serializer output
        data = serializer.data

        # Check renamed fields
        self.assertIn("post_title", data)
        self.assertEqual(data["post_title"], "Test Post")

        # Check nested author and user
        self.assertIn("author", data)
        self.assertIn("bio", data["author"])
        self.assertIn("user", data["author"])
        self.assertIn("username", data["author"]["user"])
        self.assertEqual(data["author"]["user"]["username"], "user1")

        # Check that tags and categories are properly serialized
        self.assertIn("tags", data)
        self.assertTrue(len(data["tags"]) > 0)
        self.assertEqual(data["tags"][0]["name"], "Django")

        self.assertIn("categories", data)
        self.assertTrue(len(data["categories"]) > 0)
        self.assertEqual(data["categories"][0]["name"], "Technology")
