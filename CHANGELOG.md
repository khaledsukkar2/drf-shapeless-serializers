# Changelog

All notable changes to this project will be documented in this file.

## [1.0.8] - 2026-01-12

### Added
- **Nested Syntax**: Added support for passing instantiated serializers in the `nested` configuration. This allows for a more pythonic, type-safe, and cleaner syntax compared to the dictionary-based approach. 
- **ShapelessViewMixin**: Introduced `ShapelessViewMixin` for Class-Based Views (ViewSets, GenericAPIView). This mixin automatically injects dynamic configuration (fields, nested, etc.) into the serializer, simplifying controller logic.
- **Improved Test Suite**: Added more tests for nested relationships and DRF view classes to ensure robustness.

### Changed
- Updated documentation to reflect the new nested syntax and mixin usage.
- Refactored `DynamicNestedSerializerMixin` to handle serializer instances.

## [1.0.7] - 2025-07-20

### Added
- **InlineShapelessModelSerializer**: Added `InlineShapelessModelSerializer` to create model serializers on-the-fly without defining a class. Contributed by [Hussain Khallouf](https://github.com/hussain-khallouf-ite).
