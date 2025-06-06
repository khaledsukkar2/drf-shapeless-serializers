import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import serializers
from rest_framework.test import APIRequestFactory

from shapeless_serializers.mixins import DynamicSerializerConfigError
from shapeless_serializers.serializers import ShapelessModelSerializer
from test_app.models import AuthorProfile, BlogPost, Category, Comment, PostLike, Tag
from test_app.serializers import (
    DynamicAuthorProfileSerializer,
    DynamicBlogPostSerializer,
    DynamicCommentSerializer,
    UserSerializer,
)

User = get_user_model()


class AuthorProfileSnazzySerializer(ShapelessModelSerializer):
    computed_field = serializers.SerializerMethodField()

    class Meta:
        model = AuthorProfile
        fields = [
            "id",
            "bio",
            "website",
            "is_verified",
            "joined_date",
            "computed_field",
        ]

    def get_computed_field(self, obj):
        return f"Computed: {obj.user.username}"


class TestShaplessModelSerializer(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(
            username="testuser", email="user@example.com", password="password"
        )
        self.staff_user = User.objects.create_user(
            username="staff",
            email="staff@example.com",
            password="password",
            is_staff=True,
        )
        self.author = AuthorProfile.objects.create(
            user=self.user,
            bio="Experienced developer",
            website="https://example.com",
            is_verified=True,
        )
        self.request = self.factory.get("/profile/")
        self.request.user = self.user

        self.user1 = User.objects.create_user(username="user1", password="password1")
        self.user2 = User.objects.create_user(username="user2", password="password2")
        self.user3 = User.objects.create_user(username="user3", password="password3")

        self.author_profile1 = AuthorProfile.objects.create(
            user=self.user1, bio="Bio for user1", website="http://user1.com"
        )
        self.author_profile2 = AuthorProfile.objects.create(
            user=self.user2, bio="Bio for user2"
        )

        self.category1 = Category.objects.create(name="Technology")
        self.category2 = Category.objects.create(name="Science")
        self.category3 = Category.objects.create(name="Fiction")

        self.tag1 = Tag.objects.create(name="Python")
        self.tag2 = Tag.objects.create(name="Django")
        self.tag3 = Tag.objects.create(name="AI")
        self.tag4 = Tag.objects.create(name="Machine Learning")

        self.post1 = BlogPost.objects.create(
            title="Python Tech Post",
            author=self.author_profile1,
            content="Content about Python and Django.",
            status="published",
            publish_date=datetime.date(2023, 1, 1),
            view_count=100,
        )
        self.post1.categories.add(self.category1)
        self.post1.tags.add(self.tag1, self.tag2)

        self.post2 = BlogPost.objects.create(
            title="AI in Science",
            author=self.author_profile2,
            content="Content about AI in science.",
            status="published",
            publish_date=datetime.date(2023, 1, 15),
            view_count=50,
        )
        self.post2.categories.add(self.category2)
        self.post2.tags.add(self.tag3, self.tag4)

        self.post3 = BlogPost.objects.create(
            title="Sci-Fi Short Story",
            author=self.author_profile1,
            content="A short fiction piece.",
            status="draft",
            publish_date=datetime.date(2023, 2, 1),
            view_count=10,
        )
        self.post3.categories.add(self.category3)
        self.post3.tags.add(self.tag3)

        self.c1_post1 = Comment.objects.create(
            post=self.post1,
            user=self.user1,
            content="Comment 1 by User 1",
            is_approved=True,
        )
        self.r1_c1 = Comment.objects.create(
            post=self.post1,
            user=self.user2,
            content="Reply 1 to C1 by User 2",
            parent=self.c1_post1,
            is_approved=True,
        )
        self.r1a_r1 = Comment.objects.create(
            post=self.post1,
            user=self.user3,
            content="Reply to R1 by User 3",
            parent=self.r1_c1,
            is_approved=True,
        )
        self.r2_c1 = Comment.objects.create(
            post=self.post1,
            user=self.user1,
            content="Reply 2 to C1 by User 1 (Unapproved)",
            parent=self.c1_post1,
            is_approved=False,
        )
        self.c2_post1 = Comment.objects.create(
            post=self.post1,
            user=self.user2,
            content="Comment 2 by User 2 (Unapproved)",
            is_approved=False,
        )
        self.c3_post1 = Comment.objects.create(
            post=self.post1,
            user=self.user3,
            content="Comment 3 by User 3",
            is_approved=True,
        )

        self.c1_post2 = Comment.objects.create(
            post=self.post2,
            user=self.user1,
            content="Comment 1 by User 1 on Post 2",
            is_approved=True,
        )
        self.r1_c1_post2 = Comment.objects.create(
            post=self.post2,
            user=self.user2,
            content="Reply 1 to C1 on Post 2 by User 2",
            parent=self.c1_post2,
            is_approved=True,
        )

        self.like1_post1 = PostLike.objects.create(post=self.post1, user=self.user1)
        self.like2_post1 = PostLike.objects.create(post=self.post1, user=self.user2)

    def test_field_selection(self):
        """Test basic field inclusion/exclusion"""
        serializer = AuthorProfileSnazzySerializer(
            instance=self.author, fields=["bio", "is_verified"]
        )
        data = serializer.data
        self.assertIn("bio", data)
        self.assertIn("is_verified", data)
        self.assertNotIn("website", data)
        self.assertNotIn("joined_date", data)

    def test_field_renaming(self):
        """Test simple field renaming"""
        serializer = AuthorProfileSnazzySerializer(
            instance=self.author,
            rename_fields={"bio": "biography", "is_verified": "verified_status"},
        )
        data = serializer.data
        self.assertIn("biography", data)
        self.assertIn("verified_status", data)
        self.assertNotIn("bio", data)
        self.assertNotIn("is_verified", data)

    def test_field_attributes(self):
        """Test modifying field attributes"""
        serializer = AuthorProfileSnazzySerializer(
            instance=self.author, field_attributes={"website": {"write_only": True}}
        )
        self.assertNotIn("website", serializer.data)

        # Verify attribute was set
        field = serializer.fields["website"]
        self.assertTrue(field.write_only)

    def test_conditional_fields(self):
        """Test conditional field inclusion"""
        condition = lambda instance, ctx: ctx["request"].user.is_staff
        serializer = AuthorProfileSnazzySerializer(
            instance=self.author,
            context={"request": self.request},
            conditional_fields={"website": condition, "joined_date": True},
        )
        data = serializer.data
        self.assertNotIn("website", data)  # Regular user - condition false
        self.assertIn("joined_date", data)  # Always true

    def test_field_selection_with_renaming(self):
        """Test field selection combined with renaming"""
        serializer = AuthorProfileSnazzySerializer(
            instance=self.author,
            fields=["bio", "is_verified"],
            rename_fields={"bio": "biography"},
        )
        data = serializer.data
        self.assertIn("biography", data)
        self.assertIn("is_verified", data)
        self.assertNotIn("bio", data)
        self.assertNotIn("website", data)

    def test_attributes_with_conditional(self):
        """Test field attributes with conditional inclusion"""
        serializer = AuthorProfileSnazzySerializer(
            instance=self.author,
            field_attributes={"website": {"write_only": True}},
            conditional_fields={"website": lambda i, c: c["request"].user.is_staff},
            context={"request": self.request},
        )
        # Regular user - field should be excluded
        data = serializer.data
        self.assertNotIn("website", data)

        # Field should still have attribute set
        field = serializer.fields["website"]
        self.assertTrue(field.write_only)

    def test_computed_field_interaction(self):
        """Test interaction with computed fields"""
        serializer = AuthorProfileSnazzySerializer(
            instance=self.author,
            fields=["bio", "computed_field"],
            rename_fields={"computed_field": "calculated"},
            conditional_fields={"calculated": True},
        )
        data = serializer.data
        self.assertIn("bio", data)
        self.assertIn("calculated", data)
        self.assertEqual(data["calculated"], f"Computed: {self.user.username}")
        self.assertNotIn("computed_field", data)

    def test_all_features_combined(self):
        """Test all mixin features working together"""
        serializer = AuthorProfileSnazzySerializer(
            instance=self.author,
            fields=["id", "bio", "website", "computed_field"],
            field_attributes={"website": {"write_only": True}},
            rename_fields={"bio": "biography", "computed_field": "calculated"},
            conditional_fields={"website": lambda i, c: c["request"].user.is_staff},
            context={"request": self.request},
        )
        data = serializer.data

        # Verify field selection
        self.assertIn("id", data)
        self.assertIn("biography", data)
        self.assertIn("calculated", data)
        self.assertNotIn("bio", data)
        self.assertNotIn("computed_field", data)
        self.assertNotIn("is_verified", data)
        self.assertNotIn("joined_date", data)

        # Verify conditional exclusion
        self.assertNotIn("website", data)  # Excluded by conditional

        # Verify field attribute
        field = serializer.fields["website"]
        self.assertTrue(field.write_only)

    def test_invalid_fields_type(self):
        """Test error for invalid fields parameter type"""
        with self.assertRaises(DynamicSerializerConfigError):
            AuthorProfileSnazzySerializer(instance=self.author, fields="not_a_list")

    def test_invalid_rename_fields_type(self):
        """Test error for invalid rename_fields type"""
        with self.assertRaises(DynamicSerializerConfigError):
            AuthorProfileSnazzySerializer(
                instance=self.author, rename_fields=["not_a_dict"]
            ).data

    def test_context_sensitive_conditional(self):
        """Test conditional that varies by context"""

        # Create condition that depends on time
        def business_hours_condition(instance, context):
            now = context["current_time"].time()
            return datetime.time(9, 0) <= now <= datetime.time(17, 0)

        # During business hours
        business_time = datetime.datetime(2023, 1, 1, 10, 0)
        serializer1 = AuthorProfileSnazzySerializer(
            instance=self.author,
            context={"current_time": business_time},
            conditional_fields={"website": business_hours_condition},
        )
        data1 = serializer1.data
        self.assertIn("website", data1)

        # Outside business hours
        non_business_time = datetime.datetime(2023, 1, 1, 18, 0)
        serializer2 = AuthorProfileSnazzySerializer(
            instance=self.author,
            context={"current_time": non_business_time},
            conditional_fields={"website": business_hours_condition},
        )
        data2 = serializer2.data
        self.assertNotIn("website", data2)

    def test_write_only_field_interaction(self):
        """Test write-only fields with dynamic features"""
        serializer = AuthorProfileSnazzySerializer(
            instance=self.author,
            fields=["id", "bio", "website"],
            field_attributes={"website": {"write_only": True}},
            rename_fields={"website": "site_url"},
        )

        data = serializer.data
        self.assertNotIn("site_url", data)
        self.assertNotIn("website", data)

    def test_callable_attribute_values(self):
        """Test callable values in field attributes"""

        def make_required(instance, context):
            return context.get("make_required", False)

        serializer = AuthorProfileSnazzySerializer(
            instance=self.author,
            context={"make_required": True},
            field_attributes={"bio": {"required": make_required}},
        )
        field = serializer.fields["bio"]
        self.assertTrue(field.required)

    def test_conditional_on_renamed_field(self):
        """Test conditional applied to renamed field"""
        serializer = AuthorProfileSnazzySerializer(
            instance=self.author,
            rename_fields={"is_verified": "verified_status"},
            conditional_fields={"is_verified": False},
        )
        data = serializer.data
        self.assertNotIn("verified_status", data)
        self.assertNotIn("is_verified", data)

    def test_complex_combined_scenario(self):
        """Test complex combination of all features with context"""
        # Staff user context
        staff_request = self.factory.get("/profile/")
        staff_request.user = self.staff_user

        # Create dynamic conditions
        def staff_condition(instance, context):
            return context["request"].user.is_staff

        def time_condition(instance, context):
            now = context["current_time"].time()
            return datetime.time(9, 0) <= now <= datetime.time(17, 0)

        # During business hours
        current_time = datetime.datetime(2023, 1, 1, 14, 0)

        serializer = AuthorProfileSnazzySerializer(
            instance=self.author,
            fields=["id", "bio", "website", "is_verified"],
            field_attributes={
                "website": {"write_only": True},
                "is_verified": {"default": False},
            },
            rename_fields={"bio": "biography", "is_verified": "verified"},
            conditional_fields={"website": staff_condition},
            context={"request": staff_request, "current_time": current_time},
        )

        # Representation checks
        data = serializer.data
        self.assertIn("id", data)
        self.assertIn("biography", data)
        self.assertNotIn("bio", data)
        self.assertNotIn("is_verified", data)
        self.assertNotIn("website", data)  # Write-only and conditional

        # Field attribute checks
        website_field = serializer.fields["website"]
        self.assertTrue(website_field.write_only)

    def test_all_fields_excluded(self):
        """Test scenario where all fields are excluded"""
        serializer = AuthorProfileSnazzySerializer(
            instance=self.author,
            fields=[],
            conditional_fields={
                "id": False,
                "bio": False,
                "website": False,
                "is_verified": False,
                "joined_date": False,
                "computed_field": False,
            },
        )
        data = serializer.data
        self.assertEqual(data, {})

    def test_invalid_field_attributes(self):
        """Test error for invalid field attributes type"""
        with self.assertRaises(DynamicSerializerConfigError):
            AuthorProfileSnazzySerializer(
                instance=self.author, field_attributes="not_a_dict"
            )

    def test_performance_with_many_fields(self):
        """Test performance with large number of fields/attributes"""
        # Create large field sets
        fields = [f"field_{i}" for i in range(1000)]
        field_attributes = {f"field_{i}": {"write_only": True} for i in range(1000)}
        rename_fields = {f"field_{i}": f"renamed_{i}" for i in range(1000)}
        conditional_fields = {f"renamed_{i}": True for i in range(1000)}

        # Add one real field
        fields.append("bio")
        field_attributes["bio"] = {"required": True}
        rename_fields["bio"] = "biography"
        conditional_fields["biography"] = True

        serializer = AuthorProfileSnazzySerializer(
            instance=self.author,
            fields=fields,
            field_attributes=field_attributes,
            rename_fields=rename_fields,
            conditional_fields=conditional_fields,
        )
        data = serializer.data

        # Only our real field should be present
        self.assertIn("biography", data)
        self.assertEqual(len(data), 1)

    def test_serializer_method_field_interaction(self):
        """Test all features with SerializerMethodField"""
        serializer = AuthorProfileSnazzySerializer(
            instance=self.author,
            fields=["id", "computed_field"],
            field_attributes={"computed_field": {"read_only": True}},
            rename_fields={"computed_field": "calculated_value"},
            conditional_fields={"calculated_value": True},
        )
        data = serializer.data

        self.assertIn("id", data)
        self.assertIn("calculated_value", data)
        self.assertEqual(data["calculated_value"], f"Computed: {self.user.username}")

        # Verify attribute was set
        field = serializer.fields["computed_field"]
        self.assertTrue(field.read_only)

    def test_deep_nested_comments_and_replies_with_filters_and_user_nesting(self):
        """
        Tests deep nesting of comments/replies including user nesting at each level,
        applying filters at multiple levels.
        Structure: BlogPost -> Comments (approved) -> Replies (approved) -> Replies (approved)
        Also, User nested at each Comment/Reply level.
        """
        serializer = DynamicBlogPostSerializer(
            self.post1,
            fields=["id", "title", "comments"],
            nested={
                "comments": {
                    "serializer": DynamicCommentSerializer,
                    "fields": ["id", "content", "user", "replies", "is_approved"],
                    "instance": (self.post1.comments.filter(is_approved=True)),
                    "many": True,
                    "nested": {
                        "user": {
                            "serializer": UserSerializer,
                            "fields": ["id", "username"],
                        },
                        "replies": {
                            "serializer": DynamicCommentSerializer,
                            "fields": ["id", "content", "user", "replies"],
                            "instance": lambda instance, ctx: instance.replies.filter(
                                is_approved=True
                            ),
                            "nested": {
                                "user": {
                                    "serializer": UserSerializer,
                                    "fields": ["id", "username"],
                                },
                                "replies": {
                                    "serializer": DynamicCommentSerializer,
                                    "fields": ["id", "content", "user"],
                                    "instance": lambda instance, ctx: instance.replies.filter(
                                        is_approved=True
                                    ),
                                    "nested": {
                                        "user": {
                                            "serializer": UserSerializer,
                                            "fields": ["id", "username"],
                                        }
                                    },
                                },
                            },
                        },
                    },
                }
            },
        )

        data = serializer.data

        self.assertEqual(data["id"], self.post1.id)
        self.assertIn("comments", data)

        self.assertEqual(len(data["comments"]), 4)
        comment_contents = {c["content"] for c in data["comments"]}
        self.assertIn("Comment 1 by User 1", comment_contents)
        self.assertIn("Comment 3 by User 3", comment_contents)
        self.assertNotIn("Comment 2 by User 2 (Unapproved)", comment_contents)

        c1_data = next(
            c for c in data["comments"] if c["content"] == "Comment 1 by User 1"
        )
        self.assertIn("user", c1_data)
        self.assertEqual(c1_data["user"]["username"], "user1")
        self.assertIn("replies", c1_data)

        self.assertEqual(len(c1_data["replies"]), 1)
        r1_data = c1_data["replies"][0]
        self.assertEqual(r1_data["content"], "Reply 1 to C1 by User 2")
        self.assertIn("user", r1_data)
        self.assertEqual(r1_data["user"]["username"], "user2")
        self.assertIn("replies", r1_data)

        self.assertEqual(len(r1_data["replies"]), 1)
        r1a_data = r1_data["replies"][0]
        self.assertEqual(r1a_data["content"], "Reply to R1 by User 3")
        self.assertIn("user", r1a_data)
        self.assertEqual(r1a_data["user"]["username"], "user3")

    def test_mixing_field_and_attribute_configs_in_deep_nesting(self):
        """
        Tests applying field, attribute, and renaming configs at different
        levels of deep nesting.
        """
        serializer = DynamicBlogPostSerializer(
            self.post1,
            fields=["id", "title", "author", "comments"],
            rename_fields={"id": "post_identifier"},
            nested={
                "author": {
                    "serializer": DynamicAuthorProfileSerializer,
                    "fields": ["bio", "is_verified"],
                    "rename_fields": {"bio": "author_biography"},
                    "field_attributes": {
                        "is_verified": {"help_text": "Verified status"}
                    },
                    "nested": {
                        "user": {
                            "serializer": UserSerializer,
                            "fields": ["id", "username"],
                            "rename_fields": {"username": "user_login"},
                        }
                    },
                },
                "comments": {
                    "serializer": DynamicCommentSerializer,
                    "fields": ["id", "content", "user", "replies"],
                    "instance": self.post1.comments.filter(
                        is_approved=True, parent__isnull=True
                    ),
                    "rename_fields": {"content": "comment_text"},
                    "field_attributes": {"id": {"label": "Comment ID"}},
                    "nested": {
                        "user": {
                            "serializer": UserSerializer,
                            "fields": ["id", "username"],
                            "rename_fields": {"username": "commenter_name"},
                        },
                        "replies": {
                            "serializer": DynamicCommentSerializer,
                            "fields": ["id", "content", "user"],
                            "instance": lambda instance, ctx: instance.replies.filter(
                                is_approved=True
                            ),
                            "rename_fields": {"content": "reply_text"},
                            "field_attributes": {"id": {"label": "Reply ID"}},
                            "nested": {
                                "user": {
                                    "serializer": UserSerializer,
                                    "fields": ["id", "username"],
                                    "rename_fields": {"username": "replier_name"},
                                }
                            },
                        },
                    },
                },
            },
        )
        data = serializer.data
        self.assertIn("post_identifier", data)
        self.assertNotIn("id", data)
        self.assertEqual(data["post_identifier"], self.post1.id)
        self.assertIn("author", data)
        self.assertIn("comments", data)

        author_data = data["author"]
        self.assertIn("author_biography", author_data)
        self.assertNotIn("bio", author_data)
        self.assertEqual(author_data["author_biography"], "Bio for user1")
        self.assertIn("is_verified", author_data)
        self.assertEqual(author_data["is_verified"], False)

        self.assertIn("user", author_data)
        author_user_data = author_data["user"]
        self.assertIn("id", author_user_data)
        self.assertEqual(author_user_data["id"], self.user1.id)
        self.assertIn("user_login", author_user_data)

        self.assertEqual(len(data["comments"]), 2)
        c1_data = next(c for c in data["comments"] if c["id"] == self.c1_post1.id)

        self.assertIn("comment_text", c1_data)
        self.assertNotIn("content", c1_data)
        self.assertEqual(c1_data["comment_text"], "Comment 1 by User 1")
        self.assertIn("id", c1_data)
        self.assertEqual(c1_data["id"], self.c1_post1.id)

        self.assertIn("user", c1_data)
        comment_user_data = c1_data["user"]
        self.assertIn("id", comment_user_data)
        self.assertEqual(comment_user_data["id"], self.user1.id)
        self.assertIn("commenter_name", comment_user_data)

        self.assertIn("replies", c1_data)
        self.assertEqual(len(c1_data["replies"]), 1)
        r1_data = c1_data["replies"][0]

        self.assertIn("reply_text", r1_data)
        self.assertNotIn("content", r1_data)
        self.assertEqual(r1_data["reply_text"], "Reply 1 to C1 by User 2")
        self.assertIn("id", r1_data)
        self.assertEqual(r1_data["id"], self.r1_c1.id)

        self.assertIn("user", r1_data)
        reply_user_data = r1_data["user"]
        self.assertIn("id", reply_user_data)
        self.assertEqual(reply_user_data["id"], self.user2.id)
        self.assertIn("replier_name", reply_user_data)
        self.assertNotIn("username", reply_user_data)
        self.assertEqual(reply_user_data["replier_name"], "user2")

        