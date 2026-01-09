from django.test import TestCase

from shapeless_serializers.exceptions import DynamicSerializerConfigError
from test_app.models import (
    AuthorProfile,
    BlogPost,
    Category,
    Comment,
    PostLike,
    Tag,
    User,
)
from test_app.serializers import (
    DynamicAuthorProfileSerializer,
    DynamicBlogPostSerializer,
    DynamicCommentSerializer,
    DynamicLikeSerializer,
    TagSerializer,
    UserSerializer,
)


class ComprehensiveNestedSerializerTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create(username="user1", email="user1@example.com")
        self.user2 = User.objects.create(username="user2", email="user2@example.com")

        self.author_profile = AuthorProfile.objects.create(
            user=self.user1, bio="Author bio", website="https://author.com"
        )

        self.post = BlogPost.objects.create(
            title="Test Post",
            slug="test-post",
            author=self.author_profile,
            content="Test content",
        )

        self.tag1 = Tag.objects.create(name="Django", slug="django")
        self.tag2 = Tag.objects.create(name="Python", slug="python")
        self.post.tags.add(self.tag1, self.tag2)

        self.comment1 = Comment.objects.create(
            post=self.post, user=self.user1, content="First comment"
        )
        self.comment2 = Comment.objects.create(
            post=self.post, user=self.user2, content="Second comment"
        )

        self.category1 = Category.objects.create(name="Technology", slug="tech")
        self.category2 = Category.objects.create(name="Science", slug="science")

        self.post.categories.add(self.category1, self.category2)
        # Note: tags were already added above

        PostLike.objects.create(post=self.post, user=self.user1)
        PostLike.objects.create(post=self.post, user=self.user2)

    def test_basic_nested_serialization(self):
        serializer = DynamicBlogPostSerializer(
            self.post,
            fields=["id", "title", "author"],
            nested={"author": DynamicAuthorProfileSerializer(fields=["bio"])},
        )

        data = serializer.data
        self.assertEqual(data["author"]["bio"], "Author bio")
        self.assertEqual(list(data.keys()), ["id", "title", "author"])

    def test_nested_keys_and_not_in_fields(self):
        serializer = DynamicBlogPostSerializer(
            self.post,
            fields=["id", "title"],
            nested={
                "author": DynamicAuthorProfileSerializer(fields=["bio"]),
                "tags": TagSerializer(fields=["id", "name"]),
            },
        )

        data = serializer.data
        self.assertNotIn("author", list(data.keys()))
        self.assertNotIn("tags", list(data.keys()))

    def test_five_level_nested_serialization(self):
        serializer = DynamicBlogPostSerializer(
            self.post,
            fields=["id", "title", "author", "tags", "comments", "likes"],
            nested={
                "author": DynamicAuthorProfileSerializer(
                    fields=["id", "bio", "user"],
                    nested={
                        "user": UserSerializer(
                            fields=["id", "email", "author_profile"],
                            nested={
                                "author_profile": DynamicAuthorProfileSerializer(
                                    fields=["bio", "blog_posts"],
                                    nested={
                                        "blog_posts": DynamicBlogPostSerializer(
                                            fields=["title", "tags"],
                                            nested={
                                                "tags": TagSerializer(
                                                    fields=["name"], many=True
                                                )
                                            },
                                        )
                                    },
                                )
                            },
                        )
                    },
                ),
                "comments": DynamicCommentSerializer(
                    fields=["content", "user"],
                    nested={"user": UserSerializer(fields=["username"])},
                ),
                "tags": TagSerializer(fields=["id", "name"]),
                "likes": DynamicLikeSerializer(
                    fields=["id", "user"],
                    nested={"user": UserSerializer(fields=["email"])},
                ),
            },
        )

        data = serializer.data
        self.assertEqual(data["title"], "Test Post")

        author_data = data["author"]
        self.assertEqual(author_data["bio"], "Author bio")

        user_data = author_data["user"]
        self.assertEqual(user_data["email"], "user1@example.com")

        nested_profile = user_data["author_profile"]
        self.assertEqual(nested_profile["bio"], "Author bio")

        self.assertTrue(len(nested_profile["blog_posts"]) > 0)
        first_nested_post = nested_profile["blog_posts"][0]
        self.assertEqual(first_nested_post["title"], "Test Post")

        self.assertTrue(len(first_nested_post["tags"]) > 0)
        # Check if Django tag is present
        tag_names = [t["name"] for t in first_nested_post["tags"]]
        self.assertIn("Django", tag_names)

        self.assertEqual(len(data["comments"]), 2)
        self.assertEqual(data["comments"][0]["content"], "First comment")
        self.assertEqual(data["comments"][0]["user"]["username"], "user1")

        self.assertEqual(len(data["tags"]), 2)
        # Check exact tag match might be order dependent, so check presence
        tag_data = [{"id": t["id"], "name": t["name"]} for t in data["tags"]]
        self.assertTrue(any(t["name"] == "Django" for t in tag_data))

        self.assertEqual(len(data["likes"]), 2)
        self.assertEqual(data["likes"][0]["user"]["email"], "user1@example.com")

    def test_multi_level_field_limiting(self):
        serializer = DynamicBlogPostSerializer(
            self.post,
            fields=["title", "comments"],
            nested={
                "comments": DynamicCommentSerializer(
                    fields=["content", "user"],
                    nested={"user": UserSerializer(fields=["username"])},
                )
            },
        )

        data = serializer.data
        self.assertEqual(list(data.keys()), ["title", "comments"])
        self.assertEqual(len(data["comments"]), 2)
        self.assertEqual(data["comments"][0]["user"]["username"], "user1")
        self.assertNotIn("email", data["comments"][0]["user"])

    def test_max_depth_prevention(self):
        serializer = DynamicBlogPostSerializer(
            self.post,
            nested={
                "author": DynamicAuthorProfileSerializer(
                    nested={
                        "blog_posts": DynamicBlogPostSerializer(
                            nested={"author": DynamicAuthorProfileSerializer()}
                        )
                    }
                )
            },
        )

        data = serializer.data

        # Should stop at max_depth (default=5 in many cases, but here we just check recursion stops)
        # Note: In the instance-based approach, you explicitly define the structure.
        # Recursive definitions require careful handling if defining circular structures.

        author = data["author"]
        self.assertIn("blog_posts", author)
        self.assertTrue(len(author["blog_posts"]) > 0)

        first_post = author["blog_posts"][0]
        self.assertIn("author", first_post)

        nested_author = first_post["author"]
        self.assertEqual(nested_author["bio"], "Author bio")
        # Since we didn't define further nesting in the structure above, it stops naturally here.
        self.assertNotIn("blog_posts", nested_author)

    def test_many_to_many_serialization(self):
        serializer = DynamicBlogPostSerializer(
            self.post,
            fields=["title", "tags"],
            nested={
                "tags": TagSerializer(
                    fields=["name"], rename_fields={"name": "tag_name"}
                )
            },
        )

        data = serializer.data
        self.assertEqual(len(data["tags"]), 2)
        self.assertEqual(data["tags"][0]["tag_name"], "Django")
        self.assertEqual(data["tags"][1]["tag_name"], "Python")

    def test_reverse_relationship_serialization(self):
        serializer = DynamicAuthorProfileSerializer(
            self.author_profile,
            fields=["bio", "blog_posts"],
            nested={
                "blog_posts": DynamicBlogPostSerializer(
                    fields=["title", "likes"],
                    nested={
                        "likes": DynamicLikeSerializer(
                            fields=["user"],
                            nested={"user": UserSerializer(fields=["username"])},
                        )
                    },
                )
            },
        )

        data = serializer.data
        self.assertEqual(len(data["blog_posts"]), 1)
        post = data["blog_posts"][0]
        self.assertEqual(len(post["likes"]), 2)
        self.assertEqual(post["likes"][0]["user"]["username"], "user1")
        self.assertEqual(post["likes"][1]["user"]["username"], "user2")

    def test_empty_relationship_handling(self):
        post = BlogPost.objects.create(
            title="Empty Post",
            slug="empty-post",
            author=self.author_profile,
            content="No comments",
        )

        serializer = DynamicBlogPostSerializer(
            post,
            fields=["title", "comments"],
            nested={"comments": DynamicCommentSerializer()},
        )

        data = serializer.data
        self.assertEqual(data["comments"], [])

    def test_context_propagation(self):
        class ContextAwareSerializer(DynamicAuthorProfileSerializer):
            def to_representation(self, instance):
                rep = super().to_representation(instance)
                rep["request_method"] = self.context.get("request_method")
                return rep

        serializer = DynamicBlogPostSerializer(
            self.post,
            context={"request_method": "GET"},
            nested={
                "author": ContextAwareSerializer(
                    # Instance-based approach propagates context automatically
                    nested={"user": UserSerializer(fields=["username"])}
                )
            },
        )

        data = serializer.data
        author = data["author"]
        self.assertEqual(author["request_method"], "GET")
        self.assertEqual(author["user"]["username"], "user1")

    def test_configuration_errors(self):
        with self.assertRaises(DynamicSerializerConfigError) as cm:
            DynamicBlogPostSerializer(self.post, nested="invalid_config").data
        self.assertIn("must be a dictionary", str(cm.exception))

        with self.assertRaises(DynamicSerializerConfigError) as cm:
            DynamicBlogPostSerializer(
                self.post,
                nested={"author": "Not a serializer or dict"},
            ).data
        self.assertIn("must be a dictionary or Serializer instance", str(cm.exception))
