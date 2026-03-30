"""Root URL configuration."""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)

from health.views import health_check

urlpatterns = [
    # ── Django admin ──────────────────────────────────────────────────────────
    path('admin/', admin.site.urls),

    # ── Health check (no auth, used by load balancers / k8s probes) ──────────
    path('api/health/', health_check, name='health-check'),

    # ── OpenAPI schema + Swagger UI ───────────────────────────────────────────
    path('api/schema/', SpectacularAPIView.as_view(), name='api-schema'),
    path(
        'api/docs/',
        SpectacularSwaggerView.as_view(url_name='api-schema'),
        name='api-docs',
    ),

    # ── Versioned API (v1) ────────────────────────────────────────────────────
    path('api/v1/user/',   include('user.urls')),
    path('api/v1/recipe/', include('recipe.urls')),

    # ── Unversioned aliases (backwards-compatible, deprecated) ───────────────
    path('api/user/',   include('user.urls')),
    path('api/recipe/', include('recipe.urls')),
]

# In development Django serves uploaded media files.
# In production Nginx handles /static/media/ from the shared volume.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
