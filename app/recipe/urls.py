"""URL mappings for the recipe app."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from recipe import views

router = DefaultRouter()
router.register('recipes',     views.RecipeViewSet)
router.register('tags',        views.TagViewSet)
router.register('ingredients', views.IngredientViewSet)

app_name = 'recipe'

urlpatterns = [
    path('', include(router.urls)),
    path('feed/',                          views.FeedView.as_view(),              name='feed'),
    path('discover/',                      views.DiscoverView.as_view(),           name='discover'),
    path('recipes/<int:pk>/public/',       views.RecipePublicDetailView.as_view(), name='recipe-public-detail'),
]
