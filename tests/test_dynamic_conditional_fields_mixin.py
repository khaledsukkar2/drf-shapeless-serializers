from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils.timezone import datetime
from rest_framework import serializers
from rest_framework.test import APIRequestFactory

from test_app.models import AuthorProfile, BlogPost, Category, Comment
from shapeless_serializers.mixins import (
    DynamicConditionalFieldsMixin,
    DynamicSerializerConfigError,
)

User = get_user_model()


class AuthorProfileSerializer(
    DynamicConditionalFieldsMixin, serializers.ModelSerializer
):
    class Meta:
        model = AuthorProfile
        fields = ["id", "bio", "website", "is_verified", "joined_date"]


class CategorySerializer(DynamicConditionalFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "slug", "description"]


class CommentSerializer(DynamicConditionalFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ["id", "content", "created_at", "is_approved"]


class BlogPostSerializer(DynamicConditionalFieldsMixin, serializers.ModelSerializer):
    author = AuthorProfileSerializer()
    categories = CategorySerializer(many=True)
    comments = CommentSerializer(many=True, source="comments.all")

    class Meta:
        model = BlogPost
        fields = [
            "id",
            "title",
            "slug",
            "content",
            "status",
            "publish_date",
            "author",
            "categories",
            "comments",
            "view_count",
        ]


class DynamicConditionalFieldsMixinTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

        self.user = User.objects.create_user(
            username="testuser", email="user@example.com", password="password"
        )
        self.admin = User.objects.create_user(
            username="admin",
            email="admin@example.com",
            password="password",
            is_staff=True,
        )

        self.author = AuthorProfile.objects.create(
            user=self.user,
            bio="Experienced developer",
            website="https://example.com",
            is_verified=True,
        )

        self.tech_category = Category.objects.create(
            name="Technology", slug="technology"
        )
        self.science_category = Category.objects.create(name="Science", slug="science")

        self.blog_post = BlogPost.objects.create(
            title="Django REST Framework Tips",
            author=self.author,
            content="Advanced serialization techniques",
            slug="django-tips",
            status="published",
            publish_date=datetime.now(),
        )
        self.blog_post.categories.add(self.tech_category, self.science_category)

        self.comment1 = Comment.objects.create(
            post=self.blog_post, user=self.user, content="Great post!", is_approved=True
        )
        self.comment2 = Comment.objects.create(
            post=self.blog_post,
            user=self.admin,
            content="Needs more examples",
            is_approved=False,
        )

        self.request = self.factory.get("/posts/")
        self.request.user = self.user

    def test_boolean_condition_true(self):
        """Test field inclusion with boolean True condition"""
        serializer = BlogPostSerializer(
            instance=self.blog_post, conditional_fields={"view_count": True}
        )
        data = serializer.data
        self.assertIn("view_count", data)

    def test_boolean_condition_false(self):
        """Test field exclusion with boolean False condition"""
        serializer = BlogPostSerializer(
            instance=self.blog_post, conditional_fields={"title": False}
        )
        data = serializer.data
        self.assertNotIn("title", data)

    def test_callable_condition_true(self):
        """Test field inclusion with callable returning True"""
        condition = lambda instance, ctx: instance.status == "published"
        serializer = BlogPostSerializer(
            instance=self.blog_post, conditional_fields={"slug": condition}
        )
        data = serializer.data
        self.assertIn("slug", data)

    def test_callable_condition_false(self):
        """Test field exclusion with callable returning False"""
        condition = lambda instance, ctx: ctx["request"].user.is_staff
        serializer = BlogPostSerializer(
            instance=self.blog_post,
            context={"request": self.request},
            conditional_fields={"content": condition},
        )
        data = serializer.data
        self.assertNotIn("content", data)

    def test_multiple_conditions(self):
        """Test multiple fields with different conditions"""
        serializer = BlogPostSerializer(
            instance=self.blog_post,
            context={"request": self.request},
            conditional_fields={
                "title": True,
                "slug": False,
                "view_count": lambda i, c: c["request"].user.is_staff,
            },
        )
        data = serializer.data
        self.assertIn("title", data)
        self.assertNotIn("slug", data)
        self.assertNotIn("view_count", data)

    def test_non_existent_field_condition(self):
        """Test condition on non-existent field (should be ignored)"""
        serializer = BlogPostSerializer(
            instance=self.blog_post, conditional_fields={"non_existent_field": True}
        )
        data = serializer.data
        # Should not raise error
        self.assertIn("title", data)

    def test_invalid_conditional_fields_type(self):
        """Test error when conditional_fields is not a dictionary"""
        with self.assertRaises(Exception) as cm:
            BlogPostSerializer(
                instance=self.blog_post, conditional_fields=["not_a_dict"]
            ).data
        self.assertIn("must be a dictionary", str(cm.exception))

    def test_none_conditional_fields(self):
        """Test behavior when conditional_fields is None"""
        serializer = BlogPostSerializer(
            instance=self.blog_post, conditional_fields=None
        )
        data = serializer.data
        self.assertIn("title", data)
        self.assertIn("content", data)

    def test_empty_conditional_fields(self):
        """Test behavior with empty conditional_fields dictionary"""
        serializer = BlogPostSerializer(instance=self.blog_post, conditional_fields={})
        data = serializer.data
        self.assertIn("title", data)
        self.assertIn("content", data)

    def test_condition_callable_exception(self):
        """Test error handling when condition callable raises exception"""

        def failing_condition(instance, context):
            raise ValueError("Simulated error")

        with self.assertRaises(DynamicSerializerConfigError) as cm:
            BlogPostSerializer(
                instance=self.blog_post, conditional_fields={"title": failing_condition}
            ).data
        self.assertIn("Error evaluating condition", str(cm.exception))
        self.assertIn("Simulated error", str(cm.exception))

    def test_condition_non_boolean_callable(self):
        """Test non-boolean return from callable (should use truthiness)"""
        serializer = BlogPostSerializer(
            instance=self.blog_post,
            conditional_fields={
                "title": lambda i, c: "truthy string",
                "slug": lambda i, c: 0,
            },
        )
        data = serializer.data
        self.assertIn("title", data)  # "truthy string" is truthy
        self.assertNotIn("slug", data)  # 0 is falsy

    def test_condition_with_serializer_method_field(self):
        """Test conditional field with serializer method field"""

        class MethodFieldSerializer(
            DynamicConditionalFieldsMixin, serializers.ModelSerializer
        ):
            custom_field = serializers.SerializerMethodField()

            class Meta:
                model = BlogPost
                fields = ["id", "title", "custom_field"]

            def get_custom_field(self, obj):
                return f"Custom: {obj.title}"

        serializer = MethodFieldSerializer(
            instance=self.blog_post, conditional_fields={"custom_field": True}
        )
        data = serializer.data
        self.assertIn("custom_field", data)

        serializer = MethodFieldSerializer(
            instance=self.blog_post, conditional_fields={"custom_field": False}
        )
        data = serializer.data
        self.assertNotIn("custom_field", data)

    def test_context_sensitive_condition(self):
        """Test condition that depends on request context"""

        def staff_only(instance, context):
            return context["request"].user.is_staff

        # Regular user
        self.request.user = self.user
        user_serializer = BlogPostSerializer(
            instance=self.blog_post,
            context={"request": self.request},
            conditional_fields={"view_count": staff_only},
        )
        user_data = user_serializer.data
        self.assertNotIn("view_count", user_data)

        # Admin user
        self.request.user = self.admin
        admin_serializer = BlogPostSerializer(
            instance=self.blog_post,
            context={"request": self.request},
            conditional_fields={"view_count": staff_only},
        )
        admin_data = admin_serializer.data
        self.assertIn("view_count", admin_data)

    def test_condition_with_complex_context(self):
        """Test condition using multiple context elements"""

        def complex_condition(instance, context):
            return context["request"].user == instance.author.user and context.get(
                "show_details", False
            )

        # Context doesn't meet condition
        serializer1 = BlogPostSerializer(
            instance=self.blog_post,
            context={"request": self.request, "show_details": False},
            conditional_fields={"slug": complex_condition},
        )
        data1 = serializer1.data
        self.assertNotIn("slug", data1)

        # Context meets condition
        serializer2 = BlogPostSerializer(
            instance=self.blog_post,
            context={"request": self.request, "show_details": True},
            conditional_fields={"slug": complex_condition},
        )
        data2 = serializer2.data
        self.assertIn("slug", data2)

    def test_condition_with_sensitive_data(self):
        """Test that sensitive data can be conditionally excluded"""

        class UserSerializer(
            DynamicConditionalFieldsMixin, serializers.ModelSerializer
        ):
            class Meta:
                model = User
                fields = ["id", "username", "password", "email"]

        # Condition: never show password
        serializer = UserSerializer(
            instance=self.user, conditional_fields={"password": False}
        )
        data = serializer.data
        self.assertNotIn("password", data)

    def test_condition_preventing_data_leakage(self):
        """Test condition preventing data leakage between users"""

        def owner_only(instance, context):
            return context["request"].user == instance.user

        # Create comment by another user
        other_user = User.objects.create_user(username="other", password="pass")
        comment = Comment.objects.create(
            post=self.blog_post, user=other_user, content="Private comment"
        )

        # Request as comment owner
        request = self.factory.get("/")
        request.user = other_user
        serializer1 = CommentSerializer(
            instance=comment,
            context={"request": request},
            conditional_fields={"content": owner_only},
        )
        data1 = serializer1.data
        self.assertIn("content", data1)

        # Request as different user
        request.user = self.user
        serializer2 = CommentSerializer(
            instance=comment,
            context={"request": request},
            conditional_fields={"content": owner_only},
        )
        data2 = serializer2.data
        self.assertNotIn("content", data2)
