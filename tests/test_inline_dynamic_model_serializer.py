from django.test import TestCase
from django.contrib.auth import get_user_model

from shapeless_serializers.serializers import InlineDynamicModelSerializer
from shapeless_serializers.exceptions import DynamicSerializerConfigError
from test_app.models import Author, Book, BlogPost, AuthorProfile, Tag, Category

User = get_user_model()


class InlineDynamicModelSerializerTests(TestCase):
    """Tests for the InlineDynamicModelSerializer class."""

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
            publication_date="2023-01-01"
        )
        
        # Create author profile
        self.author_profile = AuthorProfile.objects.create(
            user=self.user1, 
            bio="Author bio", 
            website="https://author.com"
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

    def test_inline_serializer_with_model(self):
        """Test that InlineDynamicModelSerializer correctly sets model and fields."""
        # Create an inline serializer with a model
        serializer = InlineDynamicModelSerializer(self.author1, model=Author)
        
        # Check that the serializer has the correct model and fields
        self.assertEqual(serializer.Meta.model, Author)
        self.assertEqual(serializer.Meta.fields, '__all__')
        
        # Check that the serializer data contains the expected fields
        data = serializer.data
        self.assertIn('name', data)
        self.assertIn('bio', data)
        self.assertEqual(data['name'], 'Test Author')
        self.assertEqual(data['bio'], 'Author biography')

    def test_inline_serializer_with_fields(self):
        """Test that InlineDynamicModelSerializer works with fields parameter."""
        # Create an inline serializer with a model and fields
        serializer = InlineDynamicModelSerializer(
            self.book1, 
            model=Book, 
            fields=['title', 'price']
        )
        
        # Check that the serializer data contains only the specified fields
        data = serializer.data
        self.assertIn('title', data)
        self.assertIn('price', data)
        self.assertNotIn('publication_date', data)
        self.assertEqual(data['title'], 'Test Book')
        self.assertEqual(float(data['price']), 29.99)

    def test_inline_serializer_with_nested(self):
        """Test that InlineDynamicModelSerializer works with nested parameter."""
        # Create an inline serializer with nested relationships
        serializer = InlineDynamicModelSerializer(
            self.book1,
            model=Book,
            fields=['title', 'author'],
            nested={
                'author': {
                    'serializer': InlineDynamicModelSerializer,
                    'model': Author,
                    'fields': ['name']
                }
            }
        )
        
        # Check that the serializer data contains the nested relationship
        data = serializer.data
        self.assertIn('author', data)
        self.assertIn('name', data['author'])
        self.assertEqual(data['author']['name'], 'Test Author')

    def test_inline_serializer_with_field_attributes(self):
        """Test that InlineDynamicModelSerializer works with field_attributes parameter."""
        # Create an inline serializer with field attributes
        serializer = InlineDynamicModelSerializer(
            self.author1,
            model=Author,
            field_attributes={
                'name': {'read_only': True},
                'bio': {'required': False}
            }
        )
        
        # Check that the field attributes were applied
        self.assertTrue(serializer.fields['name'].read_only)
        self.assertFalse(serializer.fields['bio'].required)

    def test_inline_serializer_with_rename_fields(self):
        """Test that InlineDynamicModelSerializer works with rename_fields parameter."""
        # Create an inline serializer with renamed fields
        serializer = InlineDynamicModelSerializer(
            self.author1,
            model=Author,
            rename_fields={'name': 'author_name', 'bio': 'biography'}
        )
        
        # Check that the fields were renamed in the output
        data = serializer.data
        self.assertIn('author_name', data)
        self.assertIn('biography', data)
        self.assertNotIn('name', data)
        self.assertNotIn('bio', data)
        self.assertEqual(data['author_name'], 'Test Author')
        self.assertEqual(data['biography'], 'Author biography')

    def test_inline_serializer_with_conditional_fields(self):
        """Test that InlineDynamicModelSerializer works with conditional_fields parameter."""
        # Create an inline serializer with conditional fields
        serializer = InlineDynamicModelSerializer(
            self.author1,
            model=Author,
            conditional_fields={
                'bio': False  # Exclude bio field
            }
        )
        
        # Check that the conditional fields were applied
        data = serializer.data
        self.assertIn('name', data)
        self.assertNotIn('bio', data)

    def test_inline_serializer_without_model(self):
        """Test that InlineDynamicModelSerializer works without model parameter."""
        # Create a subclass with Meta class
        class AuthorInlineSerializer(InlineDynamicModelSerializer):
            class Meta:
                model = Author
                fields = ['name']
        
        # Create an instance of the serializer
        serializer = AuthorInlineSerializer(self.author1)
        
        # Check that the serializer data contains the expected fields
        data = serializer.data
        self.assertIn('name', data)
        self.assertNotIn('bio', data)
        self.assertEqual(data['name'], 'Test Author')

    def test_inline_serializer_many_true(self):
        """Test that InlineDynamicModelSerializer works with many=True."""
        # Create multiple authors
        author2 = Author.objects.create(name="Second Author", bio="Another biography")
        authors = [self.author1, author2]
        
        # Create an inline serializer with many=True
        serializer = InlineDynamicModelSerializer(
            authors,
            model=Author,
            many=True,
            fields=['name']
        )
        
        # Check that the serializer data contains multiple items
        data = serializer.data
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['name'], 'Test Author')
        self.assertEqual(data[1]['name'], 'Second Author')

    def test_inline_serializer_complex_case(self):
        """Test a complex case with multiple features combined."""
        # Create an inline serializer with multiple features
        serializer = InlineDynamicModelSerializer(
            self.post,
            model=BlogPost,
            fields=['title', 'content', 'author', 'tags', 'categories'],
            nested={
                'author': {
                    'serializer': InlineDynamicModelSerializer,
                    'model': AuthorProfile,
                    'fields': ['bio', 'user'],
                    'nested': {
                        'user': {
                            'serializer': InlineDynamicModelSerializer,
                            'model': User,
                            'fields': ['username', 'email']
                        }
                    }
                },
                'tags': {
                    'serializer': InlineDynamicModelSerializer,
                    'model': Tag,
                    'fields': ['name'],
                    'many': True
                },
                'categories': {
                    'serializer': InlineDynamicModelSerializer,
                    'model': Category,
                    'fields': ['name'],
                    'many': True
                }
            },
            rename_fields={'title': 'post_title'}
        )
        
        # Check the complex serializer output
        data = serializer.data
        
        # Check renamed fields
        self.assertIn('post_title', data)
        self.assertEqual(data['post_title'], 'Test Post')
        
        # Check nested author and user
        self.assertIn('author', data)
        self.assertIn('bio', data['author'])
        self.assertIn('user', data['author'])
        self.assertIn('username', data['author']['user'])
        self.assertEqual(data['author']['user']['username'], 'user1')
        
        # Check that tags and categories are properly serialized
        self.assertIn('tags', data)
        self.assertIn('categories', data)