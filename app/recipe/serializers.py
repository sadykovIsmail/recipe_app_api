"""Serializers for the recipe API."""
from rest_framework import serializers

from core.models import Recipe, Tag, Ingredient, RecipeLike, RecipeComment
from django.contrib.auth import get_user_model

User = get_user_model()


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Ingredient
        fields = ['id', 'name']
        read_only_fields = ['id']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']


class RecipeAuthorSerializer(serializers.ModelSerializer):
    """Compact author info embedded in recipe responses."""
    avatar = serializers.ImageField(source='profile.avatar', read_only=True, default=None)

    class Meta:
        model  = User
        fields = ['id', 'name', 'avatar']


class RecipeSerializer(serializers.ModelSerializer):
    """List/create serializer — no description, annotated social counts."""
    tags        = TagSerializer(many=True, required=False)
    ingredients = IngredientSerializer(many=True, required=False)
    author      = RecipeAuthorSerializer(source='user', read_only=True)

    # Populated via queryset annotation
    likes_count    = serializers.IntegerField(read_only=True, default=0)
    comments_count = serializers.IntegerField(read_only=True, default=0)
    is_liked       = serializers.SerializerMethodField()

    class Meta:
        model  = Recipe
        fields = [
            'id', 'title', 'time_minutes', 'price', 'link',
            'image', 'tags', 'ingredients', 'created_at',
            'author', 'likes_count', 'comments_count', 'is_liked',
        ]
        read_only_fields = ['id', 'created_at']

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        # Use prefetched data if available, otherwise query
        if hasattr(obj, '_is_liked'):
            return obj._is_liked
        return RecipeLike.objects.filter(user=request.user, recipe=obj).exists()

    def _get_or_create_tags(self, tags, recipe):
        auth_user = self.context['request'].user
        for tag in tags:
            tag_obj, _ = Tag.objects.get_or_create(user=auth_user, **tag)
            recipe.tags.add(tag_obj)

    def _get_or_create_ingredients(self, ingredients, recipe):
        auth_user = self.context['request'].user
        for ingredient in ingredients:
            ing_obj, _ = Ingredient.objects.get_or_create(user=auth_user, **ingredient)
            recipe.ingredients.add(ing_obj)

    def create(self, validated_data):
        tags        = validated_data.pop('tags', [])
        ingredients = validated_data.pop('ingredients', [])
        recipe = Recipe.objects.create(**validated_data)
        self._get_or_create_tags(tags, recipe)
        self._get_or_create_ingredients(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        tags        = validated_data.pop('tags', None)
        ingredients = validated_data.pop('ingredients', None)
        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tags(tags, instance)
        if ingredients is not None:
            instance.ingredients.clear()
            self._get_or_create_ingredients(ingredients, instance)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class RecipeDetailSerializer(RecipeSerializer):
    """Detail serializer — adds description field."""

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['description']


class RecipeImageSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Recipe
        fields = ['id', 'image']
        read_only_fields = ['id']
        extra_kwargs = {'image': {'required': True}}


# ── Comments ──────────────────────────────────────────────────────────────────

class RecipeCommentSerializer(serializers.ModelSerializer):
    author_name   = serializers.CharField(source='user.name',           read_only=True)
    author_avatar = serializers.ImageField(source='user.profile.avatar', read_only=True, default=None)
    author_id     = serializers.IntegerField(source='user.id',          read_only=True)

    class Meta:
        model  = RecipeComment
        fields = ['id', 'text', 'created_at', 'updated_at', 'author_id', 'author_name', 'author_avatar']
        read_only_fields = ['id', 'created_at', 'updated_at']
