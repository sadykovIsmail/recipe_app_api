"""Views for the recipe API."""
from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)
from rest_framework import viewsets, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from core.models import Recipe, Tag, Ingredient
from recipe import serializers


# ── Shared authentication ─────────────────────────────────────────────────────

AUTH_CLASSES = [JWTAuthentication, TokenAuthentication]


# ── Recipe ViewSet ────────────────────────────────────────────────────────────

@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                'tags',
                OpenApiTypes.STR,
                description='Comma-separated list of tag IDs to filter by.',
            ),
            OpenApiParameter(
                'ingredients',
                OpenApiTypes.STR,
                description='Comma-separated list of ingredient IDs to filter by.',
            ),
        ]
    )
)
class RecipeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing recipes.

    Supports full CRUD, search (title/description), ordering (title, price,
    time_minutes), and filtering by tag IDs and ingredient IDs.
    Results are scoped to the authenticated user only.
    """
    serializer_class = serializers.RecipeDetailSerializer
    queryset = Recipe.objects.all()
    authentication_classes = AUTH_CLASSES
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields  = ['title', 'description']
    ordering_fields = ['title', 'price', 'time_minutes', '-id']
    ordering = ['-id']

    def get_queryset(self):
        """Return recipes for the authenticated user, with optional ID filters."""
        queryset = self.queryset.filter(user=self.request.user)

        tags_param = self.request.query_params.get('tags')
        ingredients_param = self.request.query_params.get('ingredients')

        if tags_param:
            tag_ids = [int(i) for i in tags_param.split(',') if i.strip().isdigit()]
            queryset = queryset.filter(tags__id__in=tag_ids)

        if ingredients_param:
            ing_ids = [int(i) for i in ingredients_param.split(',') if i.strip().isdigit()]
            queryset = queryset.filter(ingredients__id__in=ing_ids)

        return queryset.distinct()

    def get_serializer_class(self):
        """Use compact serializer for list, detailed for everything else."""
        if self.action == 'list':
            return serializers.RecipeSerializer
        if self.action == 'upload_image':
            return serializers.RecipeImageSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new recipe owned by the authenticated user."""
        serializer.save(user=self.request.user)

    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """Upload an image to a recipe."""
        recipe = self.get_object()
        serializer = self.get_serializer(recipe, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ── Base attribute ViewSet ────────────────────────────────────────────────────

@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                'assigned_only',
                OpenApiTypes.INT, enum=[0, 1],
                description='Filter to items assigned to at least one recipe.',
            ),
        ]
    )
)
class BaseRecipeAttrViewSet(
    mixins.DestroyModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """
    Base viewset for recipe attributes (Tags, Ingredients).
    Provides list, update, and delete — creation happens inline when
    posting a recipe with nested tag/ingredient objects.
    """
    authentication_classes = AUTH_CLASSES
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter]
    search_fields = ['name']

    def get_queryset(self):
        assigned_only = bool(int(self.request.query_params.get('assigned_only', 0)))
        queryset = self.queryset.filter(user=self.request.user)
        if assigned_only:
            queryset = queryset.filter(**{self._assigned_filter: True})
        return queryset.order_by('-name').distinct()


class TagViewSet(BaseRecipeAttrViewSet):
    """Manage tags in the database."""
    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()
    _assigned_filter = 'recipe__isnull'   # overridden in get_queryset

    def get_queryset(self):
        assigned_only = bool(int(self.request.query_params.get('assigned_only', 0)))
        queryset = self.queryset.filter(user=self.request.user)
        if assigned_only:
            queryset = queryset.filter(recipe__isnull=False)
        return queryset.order_by('-name').distinct()


class IngredientViewSet(BaseRecipeAttrViewSet):
    """Manage ingredients in the database."""
    serializer_class = serializers.IngredientSerializer
    queryset = Ingredient.objects.all()

    def get_queryset(self):
        assigned_only = bool(int(self.request.query_params.get('assigned_only', 0)))
        queryset = self.queryset.filter(user=self.request.user)
        if assigned_only:
            queryset = queryset.filter(recipe__isnull=False)
        return queryset.order_by('-name').distinct()
