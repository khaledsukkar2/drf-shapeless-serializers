from django.test import TestCase
from rest_framework import serializers

from shapeless_serializers.serializers import ShapelessSerializer



class UserData:
    def __init__(self, username, email, profile=None):
        self.username = username
        self.email = email
        self.profile = profile


class ProfileData:
    def __init__(self, bio, age):
        self.bio = bio
        self.age = age




class ProfileSerializer(ShapelessSerializer):
    bio = serializers.CharField()
    age = serializers.IntegerField()


class UserSerializer(ShapelessSerializer):
    username = serializers.CharField()
    email = serializers.EmailField()
    profile = ProfileSerializer(required=False)




class ShapelessSerializerTests(TestCase):
    def setUp(self):
        self.profile_data = ProfileData(bio="Hello World", age=30)
        self.user_data = UserData(
            username="testuser", email="test@example.com", profile=self.profile_data
        )

    def test_basic_field_selection(self):
        """Test limiting fields on a standard serializer."""
        serializer = UserSerializer(instance=self.user_data, fields=["username"])
        data = serializer.data
        self.assertEqual(data, {"username": "testuser"})
        self.assertNotIn("email", data)

    def test_field_renaming_and_attributes(self):
        """Test renaming and attribute modification."""
        serializer = UserSerializer(
            instance=self.user_data,
            fields=["username", "email"],
            rename_fields={"username": "login"},
            field_attributes={"email": {"read_only": True}},
        )
        data = serializer.data

        self.assertIn("login", data)
        self.assertEqual(data["login"], "testuser")
        self.assertIn("email", data)

        # Verify attribute application
        self.assertTrue(serializer.fields["email"].read_only)

    def test_nested_instance_pattern(self):
        """Test nesting using the direct instance pattern with non-model objects."""
        serializer = UserSerializer(
            instance=self.user_data,
            fields=["username", "profile"],
            nested={
                "profile": ProfileSerializer(
                    fields=["bio"], rename_fields={"bio": "biography"}
                )
            },
        )
        data = serializer.data

        self.assertIn("profile", data)
        self.assertIn("biography", data["profile"])
        self.assertNotIn("age", data["profile"])
        self.assertEqual(data["profile"]["biography"], "Hello World")

    def test_conditional_fields(self):
        """Test conditional inclusion/exclusion."""
        serializer = UserSerializer(
            instance=self.user_data,
            fields=["username", "email"],
            conditional_fields={"email": False},  # Always exclude
        )
        data = serializer.data
        self.assertIn("username", data)
        self.assertNotIn("email", data)

    def test_missing_data_handling(self):
        """Test handling of None/missing attributes."""
        user_no_profile = UserData(username="user2", email="user2@example.com")

        serializer = UserSerializer(
            instance=user_no_profile,
            fields=["username", "profile"],
            nested={"profile": ProfileSerializer()},
        )
        data = serializer.data
        self.assertIsNone(data["profile"])

    def test_context_passing_in_nesting(self):
        """Test that context propagates to nested instance serializers."""

        class ContextCheckSerializer(ShapelessSerializer):
            check = serializers.SerializerMethodField()

            def get_check(self, obj):
                return self.context.get("secret_key")

        serializer = UserSerializer(
            instance=self.user_data,
            context={"secret_key": "12345"},
            fields=["username", "profile"],
            nested={"profile": ContextCheckSerializer(fields=["check"])},
        )

        data = serializer.data
        self.assertEqual(data["profile"]["check"], "12345")
