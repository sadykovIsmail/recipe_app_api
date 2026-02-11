"""
Serializers for recipe API.

Serializers convert:
- Django model instances → JSON (responses)
- JSON → validated Python objects (requests)
"""
from rest_framework import serializers

# Import models used by serializers
from core.models import Recipe, Tag, Ingredient


class IngredientSerializer(serializers.ModelSerializer):
    """Serializer for ingredienst"""

    class Meta:
        model = Ingredient
        fields = ['id', 'name']
        read_only_fields = ['id']

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
    ingredients = IngredientSerializer(many=True, required=False)

    class Meta:
        model = Recipe
        # Fields exposed in API responses and accepted in requests
        fields = [
            'id', 'title', 'time_minutes', 'price', 'link', 'tags',
            'ingredients',
            ]
        # id is generated automatically
        read_only_fields = ['id']

    def _get_or_create_tags(self, tags, recipe):
        """Handle getting or creating tags as needed."""
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

    def _get_or_create_ingredients(self, ingredients, recipe):
        """Handle getting or creating ingredients as needed."""
        auth_user = self.context['request'].user
        for ingredient in ingredients:
            ingredient_obj, create = Ingredient.objects.get_or_create(
                user=auth_user,
                **ingredient,
            )
            recipe.ingredients.add(ingredient_obj)


    def create(self, validated_data):
        """
        Custom create method to handle nested tag creation.

        Default DRF create() cannot handle ManyToMany fields,
        so we override it.
        """

        # Remove tags from validated_data (ManyToMany fields
        # must be handled separately)
        tags = validated_data.pop('tags', [])
        ingredients = validated_data.pop('ingredients', [])
        # Create the recipe using remaining fields
        recipe = Recipe.objects.create(**validated_data)
        self._get_or_create_tags(tags, recipe)
        self._get_or_create_ingredients(ingredients, recipe)



        # Return the created recipe instance
        return recipe

    def update(self, instance, validate_data):
        """"Update recipe."""
        tags = validate_data.pop('tags', None)

        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tags(tags, instance)

        for attr, value in validate_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance

class RecipeDetailSerializer(RecipeSerializer):
    """
    Serializer for detailed recipe view.

    Extends RecipeSerializer by adding the description field.
    """

    class Meta(RecipeSerializer.Meta):
        # Include all fields from RecipeSerializer
        # plus the description field
        fields = RecipeSerializer.Meta.fields + ['description']
