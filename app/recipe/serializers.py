"""
Serializers for recipe API.

Serializers convert:
- Django model instances → JSON (responses)
- JSON → validated Python objects (requests)
"""
from rest_framework import serializers

# Import models used by serializers
from core.models import Recipe, Tag


class TagSerializer(serializers.ModelSerializer):
    """
    Serializer for Tag objects.

    This controls how Tag data is:
    - received from the API
    - returned in API responses
    """

    class Meta:
        model = Tag
        # Fields that will be exposed via the API
        fields = ['id', 'name']
        # id should not be editable by users
        read_only_fields = ['id']


class RecipeSerializer(serializers.ModelSerializer):
    """
    Serializer for Recipe objects.

    Used for:
    - listing recipes
    - creating recipes
    """

    # Nested serializer:
    # Allows tags to be sent as a list of objects when creating a recipe
    tags = TagSerializer(many=True, required=False)

    class Meta:
        model = Recipe
        # Fields exposed in API responses and accepted in requests
        fields = ['id', 'title', 'time_minutes', 'price', 'link', 'tags']
        # id is generated automatically
        read_only_fields = ['id']

    def create(self, validated_data):
        """
        Custom create method to handle nested tag creation.

        Default DRF create() cannot handle ManyToMany fields,
        so we override it.
        """

        # Remove tags from validated_data (ManyToMany fields
        # must be handled separately)
        tags = validated_data.pop('tags', [])

        # Create the recipe using remaining fields
        recipe = Recipe.objects.create(**validated_data)

        # Get the authenticated user from the request context
        auth_user = self.context['request'].user

        # Loop through provided tags
        for tag in tags:
            # Get existing tag or create a new one for this user
            tag_obj, created = Tag.objects.get_or_create(
                user=auth_user,
                **tag,
            )
            # Attach tag to recipe (ManyToMany relationship)
            recipe.tags.add(tag_obj)

        # Return the created recipe instance
        return recipe


class RecipeDetailSerializer(RecipeSerializer):
    """
    Serializer for detailed recipe view.

    Extends RecipeSerializer by adding the description field.
    """

    class Meta(RecipeSerializer.Meta):
        # Include all fields from RecipeSerializer
        # plus the description field
        fields = RecipeSerializer.Meta.fields + ['description']
