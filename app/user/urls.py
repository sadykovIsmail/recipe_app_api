"""URL mappings for the user API."""
from django.urls import path

from user import views

app_name = 'user'

urlpatterns = [
    # ── Own account ───────────────────────────────────────────────────────────
    path('create/',         views.CreateUserView.as_view(),        name='create'),
    path('me/',             views.ManageUserView.as_view(),         name='me'),
    path('me/profile/',     views.ManageProfileView.as_view(),      name='me-profile'),
    path('me/avatar/',      views.AvatarUploadView.as_view(),       name='me-avatar'),
    path('logout/',         views.LogoutView.as_view(),             name='logout'),

    # ── JWT auth ──────────────────────────────────────────────────────────────
    path('jwt/login/',      views.JWTLoginView.as_view(),           name='jwt-login'),
    path('jwt/refresh/',    views.JWTRefreshView.as_view(),         name='jwt-refresh'),
    path('jwt/verify/',     views.JWTVerifyView.as_view(),          name='jwt-verify'),

    # ── Legacy DRF token ──────────────────────────────────────────────────────
    path('token/',          views.CreateTokenView.as_view(),        name='token'),

    # ── Social: search & profiles ─────────────────────────────────────────────
    path('search/',                  views.UserSearchView.as_view(),    name='user-search'),
    path('<int:pk>/profile/',        views.PublicProfileView.as_view(), name='user-profile'),
    path('<int:pk>/follow/',         views.FollowView.as_view(),        name='user-follow'),
    path('<int:pk>/followers/',      views.FollowersListView.as_view(), name='user-followers'),
    path('<int:pk>/following/',      views.FollowingListView.as_view(), name='user-following'),

    # ── Notifications ─────────────────────────────────────────────────────────
    path('notifications/',                 views.NotificationListView.as_view(),       name='notifications'),
    path('notifications/mark-read/',       views.NotificationMarkReadView.as_view(),   name='notifications-mark-read'),
    path('notifications/unread-count/',    views.UnreadNotificationCountView.as_view(), name='notifications-unread-count'),
]
