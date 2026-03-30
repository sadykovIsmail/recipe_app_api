"""URL mappings for the user API."""
from django.urls import path

from user import views

app_name = 'user'

urlpatterns = [
    # ── User management ───────────────────────────────────────────────────────
    path('create/', views.CreateUserView.as_view(), name='create'),
    path('me/',     views.ManageUserView.as_view(), name='me'),
    path('logout/', views.LogoutView.as_view(),     name='logout'),

    # ── JWT auth (recommended) ────────────────────────────────────────────────
    path('jwt/login/',   views.JWTLoginView.as_view(),   name='jwt-login'),
    path('jwt/refresh/', views.JWTRefreshView.as_view(), name='jwt-refresh'),
    path('jwt/verify/',  views.JWTVerifyView.as_view(),  name='jwt-verify'),

    # ── Legacy DRF token auth (backwards-compat) ──────────────────────────────
    path('token/', views.CreateTokenView.as_view(), name='token'),
]
