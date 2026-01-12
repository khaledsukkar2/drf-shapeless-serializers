
# drf-shapeless-serializers 
[![PyPI Version](https://img.shields.io/pypi/v/drf-shapeless-serializers.svg?color=success&logo=python&logoColor=white)](https://pypi.org/project/drf-shapeless-serializers/)
[![Downloads](https://static.pepy.tech/badge/drf-shapeless-serializers)](https://pepy.tech/project/drf-shapeless-serializers)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/khaledsukkar2/drf-shapeless-serializers/blob/main/LICENSE)
[![Django Packages](https://img.shields.io/badge/Published%20on-Django%20Packages-0c3c26)](https://djangopackages.org/packages/p/drf-shapeless-serializers/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
## Motivation

Traditional Django REST Framework serializers often lead to what’s known as “serializer hell” - a situation where developers:

* Create numerous serializer variations for slightly different API endpoints
* Duplicate code for simple field variations
* Struggle with rigid and complex nested relationships
* Maintain sprawling serializer classes that become hard to manage

`drf-shapeless-serializers` was created to solve these pain points by introducing dynamic runtime configuration capabilities, allowing you to eliminate up to 80% of your serializer code while gaining unprecedented flexibility.

## Documentation

[https://drf-shapeless-serializers.readthedocs.io/en/latest/](https://drf-shapeless-serializers.readthedocs.io/en/latest/)

## Overview

`drf-shapeless-serializers` provides powerful mixins that extend Django REST Framework's serializers with dynamic configuration capabilities. By inheriting from our base classes, you can select fields at runtime, rename output keys dynamically, modify field attributes per-request, and add configured nested relationships on-the-fly.

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
Instead of passing dictionaries, you now pass **instantiated serializers** into the `nested` parameter, allowing for a more Pythonic and type-safe configuration.

```python
@api_view(['GET'])
def book_detail(request, pk):
    book = Book.objects.get(pk=pk)
    serializer = BookSerializer(
        book,
        fields=['id', 'title', 'price', 'author'],
        rename_fields={'price': 'retail_price', 'id': 'book_id'},
        nested={
            'author': AuthorSerializer(
                fields=['id', 'bio', 'user'],
                rename_fields={'bio': 'biography'},
                nested={
                    'user': UserSerializer(fields=['id', 'username', 'email'])
                }
            )
        }
    )
    return Response(serializer.data)

```

## Feature Highlights

#### 1. Class-Based View (CBV) Support

The `ShapelessViewMixin` allows you to define dynamic configurations directly on your ViewSets. This keeps your view logic clean and centralized.

```python
from shapeless_serializers.views import ShapelessViewMixin

class BookViewSet(ShapelessViewMixin, viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

    def get_serializer_fields(self):
        if self.action == 'list':
            return ['id', 'title', 'price']
        return ['id', 'title', 'description', 'author', 'comments']

    def get_serializer_nested(self):
        if self.action == 'retrieve':
            return {
                'author': AuthorSerializer(fields=['name', 'bio']),
                'comments': CommentSerializer(fields=['content', 'user'], many=True)
            }
        return {}

```

#### 2. Field Selection

The `fields` parameter lets you cherry-pick exactly which fields to include.

```python
AuthorSerializer(author, fields=['id', 'name', 'birth_date'])

```

#### 3. Field Attributes

Pass standard DRF serializer params at runtime.

```python
AuthorSerializer(
    author,
    field_attributes={
        'bio': {'help_text': 'Author biography'},
        'address': {'write_only': True}
    }
)

```

#### 4. Nested Relationships

Nested configuration supports unlimited depth. Each level can be customized with its own fields, renaming, and attributes.

```python
AuthorSerializer(
    author,
    nested={
        'books': BookSerializer(
            fields=['title', 'publish_year', 'publisher'],
            nested={
                'publisher': PublisherSerializer(fields=['name', 'country'])
            }
        )
    }
)

```

For extremely complex structures, the syntax remains readable:

```python
serializer = DynamicBlogPostSerializer(
    posts,
    fields=["id", "title", "author", "comments"],
    rename_fields={"id": "post_identifier"},
    nested={
        "author": DynamicAuthorProfileSerializer(
            fields=["bio", "is_verified", "user"],
            rename_fields={"bio": "author_biography"},
            nested={
                "user": UserSerializer(
                    fields=["id", "username"],
                    rename_fields={"username": "user_login"}
                )
            }
        ),
        "comments": DynamicCommentSerializer(
            fields=["id", "content", "user", "replies"],
            instance=posts.comments.filter(is_approved=True, parent__isnull=True),
            rename_fields={"content": "comment_text"},
            nested={
                "user": UserSerializer(fields=["id", "username"]),
                "replies": DynamicCommentSerializer(
                    fields=["id", "content", "user"],
                    instance=lambda instance, ctx: instance.replies.filter(is_approved=True),
                    rename_fields={"content": "reply_text"}
                )
            }
        )
    }
)

```

#### 5. Conditional Fields

Include fields based on runtime logic (like user permissions):

```python
AuthorSerializer(
    author,
    conditional_fields={
        'email': lambda instance, ctx: ctx['request'].user.is_staff
    }
)

```

#### 6. Inline Shapeless Model Serializers

Create serializers on-the-fly without defining a class—perfect for one-off needs:

```python
serializer = InlineShapelessModelSerializer(
    book,
    model=Book,
    fields=['title', 'author'],
    nested={
        'author': InlineShapelessModelSerializer(
            model=Author,
            fields=['name', 'bio']
        )
    }
)

```

## When to Use

* Building public APIs with multiple versions.
* Projects needing different "views" of the same data (e.g., Summary vs. Detail).
* Rapidly evolving API requirements where creating new classes is a bottleneck.
* Any project suffering from "Serializer Bloat."

## Contributing

We welcome contributions! Please check the `CONTRIBUTING.md` file.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Acknowledgements

Inspired by the need for high-flexibility API systems. Special thanks to the Django REST Framework community.

---

## Support Me

If you find this package useful, please consider supporting its development:

*   **USDT (TRC20)**: `TEitNDQMm4upYmNvFeMpxTRGEJGdord3S5`
*   **USDT (BEP20)**: `0xc491a2ba6f386ddbf26cdc906939230036473f5d`
*   **BTC**: `13X8aZ23pFNCH2FPW6YpRTw4PGxo7AvFkN`



