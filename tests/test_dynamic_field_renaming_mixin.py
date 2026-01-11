from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import serializers
from rest_framework.test import APIRequestFactory

from shapeless_serializers.mixins.serializers import (
    DynamicFieldRenamingMixin,
    DynamicSerializerConfigError,
)
from test_app.models import AuthorProfile, BlogPost, Category

User = get_user_model()


class AuthorProfileSerializer(DynamicFieldRenamingMixin, serializers.ModelSerializer):
    class Meta:
        model = AuthorProfile
        fields = ["id", "bio", "website", "is_verified"]


class CategorySerializer(DynamicFieldRenamingMixin, serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "slug"]


class BlogPostSerializer(DynamicFieldRenamingMixin, serializers.ModelSerializer):
    author = AuthorProfileSerializer()
    categories = CategorySerializer(many=True)

    class Meta:
        model = BlogPost
        fields = ["id", "title", "content", "author", "categories"]


class DynamicFieldRenamingMixinTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

        self.user = User.objects.create_user(username="testuser", password="password")
        self.staff_user = User.objects.create_user(
            username="staff", password="password", is_staff=True
        )

        self.author_profile = AuthorProfile.objects.create(
            user=self.user,
            bio="Experienced developer",
            website="https://example.com",
            is_verified=True,
        )

        self.category1 = Category.objects.create(name="Technology", slug="technology")
        self.category2 = Category.objects.create(name="Science", slug="science")

        self.blog_post = BlogPost.objects.create(
            title="Django REST Framework Tips",
            author=self.author_profile,
            content="Advanced serialization techniques",
            slug="django-tips",
        )
        self.blog_post.categories.add(self.category1, self.category2)

        self.request = self.factory.get("/posts/")
        self.request.user = self.user

    def test_single_field_renaming(self):
        """Test renaming a single top-level field"""
        serializer = BlogPostSerializer(
            instance=self.blog_post,
            context={"request": self.request},
            rename_fields={"title": "post_title"},
        )
        data = serializer.data

        self.assertIn("post_title", data)
        self.assertEqual(data["post_title"], "Django REST Framework Tips")
        self.assertNotIn("title", data)

    def test_multiple_field_renaming(self):
        """Test renaming multiple top-level fields"""
        serializer = BlogPostSerializer(
            instance=self.blog_post,
            context={"request": self.request},
            rename_fields={"title": "heading", "content": "body_text"},
        )
        data = serializer.data

        self.assertIn("heading", data)
        self.assertIn("body_text", data)
        self.assertNotIn("title", data)
        self.assertNotIn("content", data)

    def test_non_existent_field_renaming(self):
        """Test renaming non-existent fields (should be ignored)"""
        serializer = BlogPostSerializer(
            instance=self.blog_post,
            context={"request": self.request},
            rename_fields={"non_existent": "new_name", "title": "post_title"},
        )
        data = serializer.data

        self.assertIn("post_title", data)
        self.assertNotIn("non_existent", data)
        self.assertNotIn("new_name", data)

    def test_rename_to_existing_field(self):
        """Test renaming to an existing field name (should overwrite)"""
        serializer = BlogPostSerializer(
            instance=self.blog_post,
            context={"request": self.request},
            rename_fields={"title": "content"},
        )
        data = serializer.data

        self.assertEqual(data["content"], "Django REST Framework Tips")
        self.assertNotIn("title", data)
        self.assertNotEqual(data["content"], "Advanced serialization techniques")

    def test_invalid_rename_fields_type(self):
        """Test error when rename_fields is not a dictionary"""
        with self.assertRaises(DynamicSerializerConfigError) as cm:
            BlogPostSerializer(
                instance=self.blog_post, rename_fields=["not_a_dict"]
            ).data
        self.assertIn("must be a dictionary", str(cm.exception))

    def test_none_rename_fields(self):
        """Test behavior when rename_fields is None (no changes)"""
        serializer = BlogPostSerializer(
            instance=self.blog_post,
            context={"request": self.request},
            rename_fields=None,
        )
        data = serializer.data

        self.assertIn("title", data)
        self.assertIn("content", data)
        self.assertIn("author", data)
        self.assertIn("categories", data)

    def test_empty_rename_fields(self):
        """Test behavior with empty rename_fields dictionary"""
        serializer = BlogPostSerializer(
            instance=self.blog_post, context={"request": self.request}, rename_fields={}
        )
        data = serializer.data

        self.assertIn("title", data)
        self.assertIn("content", data)

    def test_serializer_method_field_renaming(self):
        """Test renaming of serializer method fields"""

        class MethodFieldSerializer(
            DynamicFieldRenamingMixin, serializers.ModelSerializer
        ):
            custom_field = serializers.SerializerMethodField()

            class Meta:
                model = BlogPost
                fields = ["id", "title", "custom_field"]

            def get_custom_field(self, obj):
                return f"Custom: {obj.title}"

        serializer = MethodFieldSerializer(
            instance=self.blog_post, rename_fields={"custom_field": "renamed_field"}
        )
        data = serializer.data

        self.assertIn("renamed_field", data)
        self.assertEqual(data["renamed_field"], "Custom: Django REST Framework Tips")
        self.assertNotIn("custom_field", data)
