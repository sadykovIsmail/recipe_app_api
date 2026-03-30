"""Views for the user API."""
from django.contrib.auth import get_user_model
from django.db.models import Count, Exists, OuterRef

from rest_framework import generics, authentication, permissions, status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView
from rest_framework import viewsets, mixins

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication

from core.models import Follow, Notification, UserProfile
from user.serializers import (
    UserSerializer,
    AuthTokenSerializer,
    EmailTokenObtainPairSerializer,
    PublicUserSerializer,
    FollowSerializer,
    UserProfileSerializer,
    NotificationSerializer,
)

User = get_user_model()
AUTH = [JWTAuthentication, authentication.TokenAuthentication]


# ── Throttles ─────────────────────────────────────────────────────────────────

class LoginRateThrottle(AnonRateThrottle):
    scope = 'login'


# ── Own account ───────────────────────────────────────────────────────────────

class CreateUserView(generics.CreateAPIView):
    """POST /api/v1/user/create/ — register a new user."""
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]


class ManageUserView(generics.RetrieveUpdateAPIView):
    """GET/PATCH /api/v1/user/me/ — retrieve or update own account."""
    serializer_class = UserSerializer
    authentication_classes = AUTH
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class ManageProfileView(generics.RetrieveUpdateAPIView):
    """GET/PATCH /api/v1/user/me/profile/ — own bio/avatar/website/location."""
    serializer_class = UserProfileSerializer
    authentication_classes = AUTH
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        profile, _ = UserProfile.objects.get_or_create(user=self.request.user)
        return profile

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)


class AvatarUploadView(APIView):
    """POST /api/v1/user/me/avatar/ — upload or replace own avatar."""
    authentication_classes = AUTH
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ── Public user search & profiles ─────────────────────────────────────────────

def _user_qs_with_stats(request_user=None):
    """Annotate User queryset with follower/following/recipe counts."""
    qs = User.objects.select_related('profile').annotate(
        followers_count=Count('followers', distinct=True),
        following_count=Count('following', distinct=True),
        recipes_count=Count('recipe', distinct=True),
    )
    return qs


class UserSearchView(generics.ListAPIView):
    """GET /api/v1/user/search/?q= — search users by name or email."""
    serializer_class = PublicUserSerializer
    authentication_classes = AUTH
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [SearchFilter]
    search_fields = ['name', 'email']

    def get_queryset(self):
        return _user_qs_with_stats(self.request.user)


class PublicProfileView(generics.RetrieveAPIView):
    """GET /api/v1/user/{id}/profile/ — public profile of any user."""
    serializer_class = PublicUserSerializer
    authentication_classes = AUTH
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return _user_qs_with_stats(self.request.user)

    def get_object(self):
        return generics.get_object_or_404(self.get_queryset(), pk=self.kwargs['pk'])


# ── Follow graph ──────────────────────────────────────────────────────────────

class FollowView(APIView):
    """
    POST   /api/v1/user/{pk}/follow/ — follow a user (idempotent)
    DELETE /api/v1/user/{pk}/follow/ — unfollow
    """
    authentication_classes = AUTH
    permission_classes = [permissions.IsAuthenticated]

    def _target(self, pk):
        return generics.get_object_or_404(User, pk=pk)

    def post(self, request, pk):
        target = self._target(pk)
        if target == request.user:
            return Response({'detail': 'You cannot follow yourself.'}, status=status.HTTP_400_BAD_REQUEST)
        Follow.objects.get_or_create(follower=request.user, following=target)
        followers_count = target.followers.count()
        return Response({'detail': 'Following.', 'followers_count': followers_count}, status=status.HTTP_201_CREATED)

    def delete(self, request, pk):
        target = self._target(pk)
        Follow.objects.filter(follower=request.user, following=target).delete()
        followers_count = target.followers.count()
        return Response({'detail': 'Unfollowed.', 'followers_count': followers_count}, status=status.HTTP_200_OK)


class FollowersListView(generics.ListAPIView):
    """GET /api/v1/user/{pk}/followers/ — who follows this user."""
    serializer_class = FollowSerializer
    authentication_classes = AUTH
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = generics.get_object_or_404(User, pk=self.kwargs['pk'])
        return User.objects.filter(following__following=user).select_related('profile')


class FollowingListView(generics.ListAPIView):
    """GET /api/v1/user/{pk}/following/ — who this user follows."""
    serializer_class = FollowSerializer
    authentication_classes = AUTH
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = generics.get_object_or_404(User, pk=self.kwargs['pk'])
        return User.objects.filter(followers__follower=user).select_related('profile')


# ── Notifications ─────────────────────────────────────────────────────────────

class NotificationListView(generics.ListAPIView):
    """GET /api/v1/user/notifications/ — own notification feed."""
    serializer_class = NotificationSerializer
    authentication_classes = AUTH
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return (
            Notification.objects
            .filter(recipient=self.request.user)
            .select_related('actor', 'actor__profile', 'recipe')
        )


class NotificationMarkReadView(APIView):
    """POST /api/v1/user/notifications/mark-read/ — mark all unread as read."""
    authentication_classes = AUTH
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        updated = Notification.objects.filter(
            recipient=request.user, is_read=False
        ).update(is_read=True)
        return Response({'marked_read': updated})


class UnreadNotificationCountView(APIView):
    """GET /api/v1/user/notifications/unread-count/ — badge count for UI."""
    authentication_classes = AUTH
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        count = Notification.objects.filter(recipient=request.user, is_read=False).count()
        return Response({'unread_count': count})


# ── JWT ───────────────────────────────────────────────────────────────────────

class JWTLoginView(TokenObtainPairView):
    """POST /api/v1/user/jwt/login/ — obtain access + refresh token pair."""
    serializer_class = EmailTokenObtainPairSerializer
    throttle_classes = [LoginRateThrottle]


class JWTRefreshView(TokenRefreshView):
    """POST /api/v1/user/jwt/refresh/ — rotate refresh token."""


class JWTVerifyView(TokenVerifyView):
    """POST /api/v1/user/jwt/verify/ — verify an access token."""


class LogoutView(APIView):
    """POST /api/v1/user/logout/ — blacklist refresh token."""
    authentication_classes = AUTH
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({'detail': 'refresh token is required.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            RefreshToken(refresh_token).blacklist()
        except Exception:
            return Response({'detail': 'Token is invalid or already blacklisted.'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'detail': 'Successfully logged out.'})


# ── Legacy token ──────────────────────────────────────────────────────────────

class CreateTokenView(ObtainAuthToken):
    """POST /api/v1/user/token/ — legacy DRF token (backwards-compat)."""
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES
    throttle_classes = [LoginRateThrottle]
