from django.test import TestCase
from rest_framework import serializers

from test_app.models import AuthorProfile, BlogPost, Category, User
from test_app.serializers import CategorySerializer
from shapeless_serializers.exceptions import DynamicSerializerConfigError
from shapeless_serializers.mixins import DynamicFieldsMixin


class AuthorProfileSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = AuthorProfile
        fields = ["id", "bio", "website", "is_verified", "joined_date"]


class BlogPostSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    secret_note = serializers.CharField(write_only=True)
    author = AuthorProfileSerializer(fields=["bio"])  # Nested with dynamic fields
    categories = CategorySerializer(many=True)

    class Meta:
        model = BlogPost
        fields = ["id", "title", "content", "secret_note", "author", "categories"]


class DynamicFieldsMixinTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="testuser")
        self.author = AuthorProfile.objects.create(
            user=self.user,
            bio="Test Bio",
            website="https://example.com",
            is_verified=True,
        )
        self.category = Category.objects.create(name="Tech", slug="tech")
        self.blog_post = BlogPost.objects.create(
            title="Test Post",
            author=self.author,
            content="Test Content",
            slug="test-post",
        )
        self.blog_post.categories.add(self.category)

    def test_no_fields_specified(self):
        serializer = AuthorProfileSerializer(instance=self.author)
        self.assertIn("bio", serializer.data)
        self.assertIn("website", serializer.data)
        self.assertIn("is_verified", serializer.data)

    def test_fields_as_list(self):
        serializer = AuthorProfileSerializer(
            instance=self.author, fields=["bio", "is_verified"]
        )
        self.assertIn("bio", serializer.data)
        self.assertIn("is_verified", serializer.data)
        self.assertNotIn("website", serializer.data)

    def test_fields_as_tuple(self):
        serializer = AuthorProfileSerializer(
            instance=self.author, fields=("bio", "is_verified")
        )
        self.assertIn("bio", serializer.data)
        self.assertIn("is_verified", serializer.data)
        self.assertNotIn("website", serializer.data)

    def test_fields_as_set(self):
        serializer = AuthorProfileSerializer(
            instance=self.author, fields={"bio", "is_verified"}
        )
        self.assertIn("bio", serializer.data)
        self.assertIn("is_verified", serializer.data)
        self.assertNotIn("website", serializer.data)

    def test_non_existent_fields(self):
        serializer = AuthorProfileSerializer(
            instance=self.author, fields=["bio", "invalid_field"]
        )
        self.assertIn("bio", serializer.data)
        self.assertNotIn("invalid_field", serializer.data)

    def test_invalid_fields_type(self):
        with self.assertRaises(DynamicSerializerConfigError):
            AuthorProfileSerializer(instance=self.author, fields="not_a_list")

    def test_write_only_fields_included(self):
        serializer = BlogPostSerializer(
            instance=self.blog_post, fields=["title", "secret_note"]
        )
        self.assertIn("title", serializer.data)
        self.assertNotIn("secret_note", serializer.data)  # Should not be visible

    def test_write_only_fields_excluded(self):
        serializer = BlogPostSerializer(
            instance=self.blog_post, fields=["title", "content"]
        )
        self.assertIn("title", serializer.data)
        self.assertNotIn("secret_note", serializer.data)
