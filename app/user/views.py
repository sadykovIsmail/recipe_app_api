"""Views for the user API."""
from rest_framework import generics, authentication, permissions, status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.views import APIView
from rest_framework.throttling import AnonRateThrottle

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication

from user.serializers import (
    UserSerializer,
    AuthTokenSerializer,
    EmailTokenObtainPairSerializer,
)


class LoginRateThrottle(AnonRateThrottle):
    """Stricter throttle applied only to the login endpoint (5/min)."""
    scope = 'login'


class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system."""
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]


class CreateTokenView(ObtainAuthToken):
    """
    Obtain a legacy DRF token (kept for backwards compatibility).
    Prefer the JWT endpoints below for new integrations.
    """
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES
    throttle_classes = [LoginRateThrottle]


class ManageUserView(generics.RetrieveUpdateAPIView):
    """Retrieve or update the authenticated user's profile."""
    serializer_class = UserSerializer
    authentication_classes = [
        JWTAuthentication,
        authentication.TokenAuthentication,
    ]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


# ── JWT endpoints ─────────────────────────────────────────────────────────────

class JWTLoginView(TokenObtainPairView):
    """
    Obtain a JWT access + refresh token pair.

    POST /api/user/jwt/login/
    Body: { "email": "...", "password": "..." }
    Returns: { "access": "...", "refresh": "..." }

    - access token valid for 15 minutes (contains name + email claims)
    - refresh token valid for 7 days (rotated on each refresh)
    """
    serializer_class = EmailTokenObtainPairSerializer
    throttle_classes = [LoginRateThrottle]


class JWTRefreshView(TokenRefreshView):
    """
    Refresh the JWT access token using a valid refresh token.

    POST /api/user/jwt/refresh/
    Body: { "refresh": "..." }
    Returns: { "access": "...", "refresh": "..." }  (refresh rotated)
    """


class JWTVerifyView(TokenVerifyView):
    """
    Verify that a JWT access token is still valid.

    POST /api/user/jwt/verify/
    Body: { "token": "..." }
    Returns: 200 OK if valid, 401 if expired/invalid
    """


class LogoutView(APIView):
    """
    Logout by blacklisting the refresh token.

    POST /api/user/logout/
    Header: Authorization: Bearer <access_token>
    Body: { "refresh": "..." }

    Blacklisting the refresh token means it can no longer be used to
    obtain new access tokens, effectively ending the session.
    """
    authentication_classes = [JWTAuthentication, authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response(
                {'detail': 'refresh token is required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception:
            return Response(
                {'detail': 'Token is invalid or already blacklisted.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response({'detail': 'Successfully logged out.'}, status=status.HTTP_200_OK)
