# Your serializers using the new mixin
from django.contrib.auth import get_user_model
from rest_framework import serializers

from test_app.models import (
    Author,
    AuthorProfile,
    BlogPost,
    Book,
    Category,
    Comment,
    PostLike,
    Tag,
)
from shapeless_serializers.serializers import ShapelessModelSerializer

User = get_user_model()


class UserSerializer(ShapelessModelSerializer):
    class Meta:
        model = User
        fields = "__all__"


class DynamicAuthorSerializer(ShapelessModelSerializer):
    class Meta:
        model = Author
        fields = "__all__"


class DynamicBookSerializer(ShapelessModelSerializer):

    class Meta:
        model = Book
        fields = "__all__"


class DynamicBlogPostSerializer(ShapelessModelSerializer):
    class Meta:
        model = BlogPost
        fields = "__all__"


class DynamicAuthorProfileSerializer(ShapelessModelSerializer):
    class Meta:
        model = AuthorProfile
        fields = "__all__"


class DynamicCommentSerializer(ShapelessModelSerializer):
    class Meta:
        model = Comment
        fields = "__all__"


class DynamicLikeSerializer(ShapelessModelSerializer):
    class Meta:
        model = PostLike
        fields = "__all__"


class TagSerializer(ShapelessModelSerializer):
    class Meta:
        model = Tag
        fields = "__all__"


class CategorySerializer(ShapelessModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"
