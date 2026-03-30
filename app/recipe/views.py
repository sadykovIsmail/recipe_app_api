"""Views for the recipe API."""
from datetime import timedelta

from django.db.models import Count, Q
from django.utils import timezone

from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiParameter, OpenApiTypes
from rest_framework import viewsets, mixins, status, generics
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from core.models import Recipe, Tag, Ingredient, RecipeLike, RecipeComment
from recipe import serializers

AUTH = [JWTAuthentication, TokenAuthentication]


# ── Helpers ───────────────────────────────────────────────────────────────────

def _annotate_recipe_qs(qs):
    """Annotate with likes_count and comments_count — eliminates N+1 queries."""
    return qs.annotate(
        likes_count=Count('likes', distinct=True),
        comments_count=Count('comments', distinct=True),
    ).select_related('user', 'user__profile').prefetch_related('tags', 'ingredients')


# ── Recipe ViewSet ────────────────────────────────────────────────────────────

@extend_schema_view(
    list=extend_schema(parameters=[
        OpenApiParameter('tags',        OpenApiTypes.STR, description='Comma-separated tag IDs'),
        OpenApiParameter('ingredients', OpenApiTypes.STR, description='Comma-separated ingredient IDs'),
    ])
)
class RecipeViewSet(viewsets.ModelViewSet):
    """
    Full CRUD on recipes.  Results scoped to authenticated user.
    Includes: search, ordering, tag/ingredient filter, image upload, likes, comments.
    """
    serializer_class = serializers.RecipeDetailSerializer
    queryset = Recipe.objects.all()
    authentication_classes = AUTH
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields   = ['title', 'description']
    ordering_fields = ['title', 'price', 'time_minutes', 'created_at', 'likes_count']
    ordering        = ['-created_at']

    def get_queryset(self):
        qs = _annotate_recipe_qs(self.queryset.filter(user=self.request.user))
        tags = self.request.query_params.get('tags')
        ings = self.request.query_params.get('ingredients')
        if tags:
            tag_ids = [int(i) for i in tags.split(',') if i.strip().isdigit()]
            qs = qs.filter(tags__id__in=tag_ids)
        if ings:
            ing_ids = [int(i) for i in ings.split(',') if i.strip().isdigit()]
            qs = qs.filter(ingredients__id__in=ing_ids)
        return qs.distinct()

    def get_serializer_class(self):
        if self.action == 'list':
            return serializers.RecipeSerializer
        if self.action == 'upload_image':
            return serializers.RecipeImageSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    # ── Image upload ──────────────────────────────────────────────────────────

    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        recipe = self.get_object()
        serializer = self.get_serializer(recipe, data=request.data)
        if serializer.is_valid():
            serializer.save()
            # Resize asynchronously — keeps the response instant
            from recipe.tasks import resize_recipe_image
            resize_recipe_image.delay(recipe.pk)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # ── Likes (toggle) ────────────────────────────────────────────────────────

    @action(methods=['POST', 'DELETE'], detail=True, url_path='like')
    def like(self, request, pk=None):
        """POST = like, DELETE = unlike. Both idempotent."""
        recipe = self.get_object()
        if request.method == 'POST':
            _, created = RecipeLike.objects.get_or_create(user=request.user, recipe=recipe)
            code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
            return Response({'liked': True, 'likes_count': recipe.likes.count()}, status=code)
        RecipeLike.objects.filter(user=request.user, recipe=recipe).delete()
        return Response({'liked': False, 'likes_count': recipe.likes.count()})

    # ── Comments ──────────────────────────────────────────────────────────────

    @action(methods=['GET', 'POST'], detail=True, url_path='comments')
    def comments(self, request, pk=None):
        recipe = self.get_object()
        if request.method == 'GET':
            qs = (
                RecipeComment.objects.filter(recipe=recipe)
                .select_related('user', 'user__profile')
            )
            page = self.paginate_queryset(qs)
            s = serializers.RecipeCommentSerializer(page, many=True)
            return self.get_paginated_response(s.data)

        serializer = serializers.RecipeCommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, recipe=recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['DELETE'], detail=True, url_path=r'comments/(?P<comment_pk>\d+)')
    def delete_comment(self, request, pk=None, comment_pk=None):
        recipe  = self.get_object()
        comment = generics.get_object_or_404(RecipeComment, pk=comment_pk, recipe=recipe)
        # Only the comment author or the recipe owner can delete
        if comment.user != request.user and recipe.user != request.user:
            return Response({'detail': 'Not allowed.'}, status=status.HTTP_403_FORBIDDEN)
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ── Feed ──────────────────────────────────────────────────────────────────────

class FeedView(generics.ListAPIView):
    """
    GET /api/v1/recipe/feed/

    Recipes from users that the authenticated user follows, newest first.
    Supports search and tag filtering.
    Cached in Redis for 60 seconds.
    """
    serializer_class = serializers.RecipeSerializer
    authentication_classes = AUTH
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields   = ['title', 'description']
    ordering_fields = ['created_at', 'likes_count']
    ordering        = ['-created_at']

    def get_queryset(self):
        following_ids = self.request.user.following.values_list('following_id', flat=True)
        qs = _annotate_recipe_qs(Recipe.objects.filter(user__in=following_ids))
        tags = self.request.query_params.get('tags')
        if tags:
            tag_ids = [int(i) for i in tags.split(',') if i.strip().isdigit()]
            qs = qs.filter(tags__id__in=tag_ids)
        return qs.distinct()


# ── Discover ──────────────────────────────────────────────────────────────────

class DiscoverView(generics.ListAPIView):
    """
    GET /api/v1/recipe/discover/

    Trending recipes from the last 7 days sorted by like count.
    No auth required — public endpoint.
    Supports search and tag filtering.
    """
    serializer_class = serializers.RecipeSerializer
    authentication_classes = AUTH
    permission_classes = [AllowAny]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields   = ['title', 'description']
    ordering_fields = ['likes_count', 'created_at']
    ordering        = ['-likes_count', '-created_at']

    def get_queryset(self):
        since = timezone.now() - timedelta(days=7)
        qs = _annotate_recipe_qs(Recipe.objects.filter(created_at__gte=since))
        tags = self.request.query_params.get('tags')
        if tags:
            tag_ids = [int(i) for i in tags.split(',') if i.strip().isdigit()]
            qs = qs.filter(tags__id__in=tag_ids)
        return qs.distinct()


# ── Tag / Ingredient ViewSets ─────────────────────────────────────────────────

@extend_schema_view(
    list=extend_schema(parameters=[
        OpenApiParameter('assigned_only', OpenApiTypes.INT, enum=[0, 1],
                         description='Filter to items assigned to at least one recipe.'),
    ])
)
class BaseRecipeAttrViewSet(
    mixins.DestroyModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    authentication_classes = AUTH
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter]
    search_fields = ['name']


class TagViewSet(BaseRecipeAttrViewSet):
    """Manage tags."""
    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()

    def get_queryset(self):
        assigned_only = bool(int(self.request.query_params.get('assigned_only', 0)))
        qs = self.queryset.filter(user=self.request.user)
        if assigned_only:
            qs = qs.filter(recipe__isnull=False)
        return qs.order_by('-name').distinct()


class IngredientViewSet(BaseRecipeAttrViewSet):
    """Manage ingredients."""
    serializer_class = serializers.IngredientSerializer
    queryset = Ingredient.objects.all()

    def get_queryset(self):
        assigned_only = bool(int(self.request.query_params.get('assigned_only', 0)))
        qs = self.queryset.filter(user=self.request.user)
        if assigned_only:
            qs = qs.filter(recipe__isnull=False)
        return qs.order_by('-name').distinct()
