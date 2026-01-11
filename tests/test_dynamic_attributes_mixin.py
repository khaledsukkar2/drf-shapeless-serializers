from django.test import TestCase
from rest_framework import serializers

from test_app.models import AuthorProfile, BlogPost, User
from test_app.serializers import DynamicAuthorProfileSerializer
from shapeless_serializers.exceptions import DynamicSerializerConfigError
from shapeless_serializers.mixins.serializers import DynamicFieldAttributesMixin


class BlogPostSerializer(DynamicFieldAttributesMixin, serializers.ModelSerializer):
    secret_note = serializers.SerializerMethodField()
    author = DynamicAuthorProfileSerializer()

    def get_secret_note(self, instance):
        return "some secret not"
    
    class Meta:
        model = BlogPost
        fields = ["id", "title", "content", "secret_note", "author"]


class DynamicFieldAttributesMixinTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="testuser")
        self.staff_user = User.objects.create(username="staff", is_staff=True)
        self.author = AuthorProfile.objects.create(user=self.user, bio="Test Bio")
        self.blog_post = BlogPost.objects.create(
            title="Test Post", author=self.author, content="Content", slug="test-post"
        )

    def test_no_field_attributes_provided(self):
        serializer = BlogPostSerializer(instance=self.blog_post)
        self.assertFalse(serializer.fields["title"].write_only)
        self.assertFalse(serializer.fields["content"].read_only)

    def test_valid_field_attributes(self):
        serializer = BlogPostSerializer(
            instance=self.blog_post,
            field_attributes={
                "title": {"write_only": True},
                "content": {"read_only": True},
            },
        )
        self.assertTrue(serializer.fields["title"].write_only)
        self.assertTrue(serializer.fields["content"].read_only)
        serializer.data
        self.assertNotIn("title", serializer.data)
        self.assertIn("content", serializer.data)

    def test_callable_attribute_values(self):
        def set_required(instance, context):
            return context.get("make_required", False)

        serializer = BlogPostSerializer(
            instance=self.blog_post,
            context={"make_required": True},
            field_attributes={"title": {"required": set_required}},
        )
        self.assertTrue(serializer.fields["title"].required)

    def test_non_existent_field(self):
        serializer = BlogPostSerializer(
            instance=self.blog_post,
            field_attributes={"invalid_field": {"write_only": True}},
        )
        self.assertNotIn("invalid_field", serializer.fields)

    def test_invalid_field_attributes_type(self):
        with self.assertRaises(DynamicSerializerConfigError):
            BlogPostSerializer(instance=self.blog_post, field_attributes="not_a_dict")

    def test_invalid_field_specific_attributes(self):
        with self.assertRaises(DynamicSerializerConfigError):
            BlogPostSerializer(
                instance=self.blog_post, field_attributes={"title": "not_a_dict"}
            )

    def test_nested_serializer_attributes(self):
        serializer = BlogPostSerializer(
            instance=self.blog_post, field_attributes={"author": {"read_only": True}}
        )
        self.assertTrue(serializer.fields["author"].read_only)

    def test_context_dependent_attributes(self):
        def set_write_only(instance, context):
            return context.get("user").is_staff

        serializer = BlogPostSerializer(
            instance=self.blog_post,
            context={"user": self.staff_user},
            field_attributes={"secret_note": {"write_only": set_write_only}},
        )
        self.assertTrue(serializer.fields["secret_note"].write_only)
