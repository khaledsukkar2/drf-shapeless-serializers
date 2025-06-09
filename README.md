
# DRF-Shapeless-Serializers Package

## Motivation

Tired of serializer hell? Every Django REST Framework developer knows the pain of creating countless serializer variations for slightly different API endpoints, duplicating code for simple field variations, struggling with rigid and complex nested relationships, and maintaining sprawling serializer classes.

What if you could eliminate 80% of your serializer code? `drf-shapeless-serializers` revolutionizes API development by giving you runtime serializer superpowers. Instead of creating multiple serializer classes , configure everything on the fly with one serializer to rule them all.
Now you can shape your serializers like Lego cubes - rearranging fields, nesting relationships, and transforming outputs dynamically with unlimited flexibility.

## Overview

`drf-shapeless-serializers`  provides powerful mixins that extend Django REST Framework's serializers with dynamic configuration capabilities. By inheriting from our base classes, you can select fields at runtime, rename output keys dynamically, modify field attributes per-request, add and configure nested relationships on-the-fly and apply conditional field logic.
All without creating multiple serializer classes and annoying nested relations. 

## Installation

```bash
pip install drf-shapeless-serializers
```

**Add to your Django settings**:
```python
INSTALLED_APPS = [
    # ... other apps
    'shapeless_serializers',
]
```

## Usage

### Basic Setup

1. **Define your shapeless serializer**:
```python
from shapeless_serializers.serializers import ShapelessModelSerializer
  
class UserSerializer(ShapelessModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class AuthorSerializer(ShapelessModelSerializer):
    class Meta:
        model = Author
        fields = '__all__'

class BookSerializer(ShapelessModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'
```

2. **Configure dynamically in views**:
```python
def book_detail(request, pk):
    book = Book.objects.get(pk=pk)
    serializer = BookSerializer(
        book,
        fields=['id', 'title', 'price', 'author'],
        rename_fields={
            'price': 'retail_price',
            'id': 'book_id'
        },
        nested={
            'author': {
                'serializer': AuthorSerializer,
                'fields': ['id', 'bio', 'user'],
                'rename_fields': {'bio': 'biography'},
                'nested': {
                    'user': {
                        'serializer': UserSerializer,
                        'fields': ['id','username', 'email'],
                    }
                }
            }
        }
    )
    return Response(serializer.data)
```

### Feature Highlights

#### 1. Field Selection
The `fields` parameter lets you cherry-pick exactly which fields to include in the output

```python
AuthorSerializer(
    author,
    fields=['id', 'name', 'birth_date']
)
```

#### 2. Field Attributes
Pass the standard DRF serializers params in run-time

```python
AuthorSerializer(
    author,
    field_attributes={
        'bio': {'help_text': 'Author biography'},
        'address' : {'write_only' : True }
    }
)
```

#### 3. Field Renaming
`rename_fields` allows you to customize the output keys without changing your models.

```python
BookSerializer(
    book,
    rename_fields={
        'price': 'retail_price',  # Output will show 'retail_price' instead of 'price'
        'id': 'book_id'
    }
)
```

#### 4. Nested Relationships
The nested serializer configuration provides ultimate flexibility for relationships. You can define unlimited nesting levels while maintaining full control over each level's behavior. The configuration supports all standard DRF parameters such as `read_only` or `instance` alongside this package-specific features, allowing you to mix and match functionality as needed. Each nested serializer can itself be configured with fields selection, renaming, and even deeper nesting - creating truly dynamic relationship trees that adapt to your API requirements.

```python
AuthorSerializer(
    author,
    nested={
        'books': {
            'serializer': BookSerializer,
            'fields': ['title', 'publish_year', 'publisher'],
            'nested': {
                'publisher': {
                    'serializer': PublisherSerializer,
                    'fields': ['name', 'country']
                }
            }
        }
    }
)
```

For complex nested structures, you can build and config relationships as deep as your API requires:

```python
 serializer = DynamicBlogPostSerializer(
            self.post1,
            fields=["id", "title", "author", "comments"],
            rename_fields={"id": "post_identifier"},
            nested={
                "author": {
                    "serializer": DynamicAuthorProfileSerializer,
                    "fields": ["bio", "is_verified", 'user'],
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
                            "instance": lambda instance, ctx: instance.replies.filter(is_approved=True)
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
```

even the very complex and deep relations are supported:
```python
serializer = DynamicBlogPostSerializer(
            BlogPost.objects.all(),
            fields=["id", "title", "author", "tags", "comments", "likes"],
            nested={
                "author": {
                    "serializer": DynamicAuthorProfileSerializer,
                    "fields": ["id", "bio", "user"],
                    "nested": {
                        "user": {
                            "serializer": UserSerializer,
                            "fields": [
                                "id",
                                "email",
                            ],
                            "nested": {
                                "author_profile": {
                                    "serializer": DynamicAuthorProfileSerializer,
                                    "fields": ["bio"],
                                    "nested": {
                                        "blog_posts": {
                                            "serializer":DynamicBlogPostSerializer,
                                            "fields": ["title"],
                                            "nested": {
                                                "tags": {
                                                    "serializer": TagSerializer,
                                                    "fields": ["name"],
                                                    "many":True,
                                                }

                                            },

                                        }

                                    },

                                }

                            },

                        }

                    },

                },
             )
```
#### 5. Conditional Fields
Choose the fields that will appear based on conditions easily:

```python
AuthorSerializer(
    author,
    conditional_fields={
        'email': lambda instance, ctx: ctx['request'].user.is_staff
    }
)
```


## WHEN TO USE

- Building public APIs with multiple versions  
- Projects needing different views of the same data
- Rapidly evolving API requirements  
- Any Django REST Framework project tired of serializer bloat

## Contributing

We welcome contributions! please check the `CONTRIBUTING.md` file

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Acknowledgements

Inspired by the flexibility needs of complex API systems. Special thanks to the Django REST Framework community for their foundational work .
