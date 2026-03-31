"""Serializers for the user API."""
from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import gettext as _

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from core.models import UserProfile, Follow, Notification


User = get_user_model()


# ── Auth ──────────────────────────────────────────────────────────────────────

class UserSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating the authenticated user."""

    class Meta:
        model = User
        fields = ('id', 'email', 'password', 'name')
        read_only_fields = ('id',)
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5}}

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user


class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the legacy DRF auth token."""
    email    = serializers.EmailField()
    password = serializers.CharField(style={'input_type': 'password'}, trim_whitespace=False)

    def validate(self, attrs):
        user = authenticate(
            request=self.context.get('request'),
            username=attrs['email'],
            password=attrs['password'],
        )
        if not user:
            raise serializers.ValidationError(
                _('Unable to authenticate with provided credentials.'),
                code='authorization',
            )
        attrs['user'] = user
        return attrs


class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    """JWT serializer that uses email and embeds name + email claims."""

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['name']  = user.name
        token['email'] = user.email
        return token


# ── Profile ───────────────────────────────────────────────────────────────────

class UserProfileSerializer(serializers.ModelSerializer):
    """Read/write serializer for UserProfile (bio, avatar, website, location)."""

    class Meta:
        model  = UserProfile
        fields = ['bio', 'avatar', 'website', 'location']


class PublicUserSerializer(serializers.ModelSerializer):
    """
    Public view of a user — shown on profile pages and in social lists.
    Includes profile fields and social stats.
    """
    bio              = serializers.CharField(source='profile.bio',      read_only=True, default='')
    avatar           = serializers.ImageField(source='profile.avatar',  read_only=True, default=None)
    website          = serializers.URLField(source='profile.website',   read_only=True, default='')
    location         = serializers.CharField(source='profile.location', read_only=True, default='')
    followers_count  = serializers.IntegerField(read_only=True)
    following_count  = serializers.IntegerField(read_only=True)
    recipes_count    = serializers.IntegerField(read_only=True)
    is_following     = serializers.SerializerMethodField()

    class Meta:
        model  = User
        fields = [
            'id', 'name', 'email', 'bio', 'avatar', 'website', 'location',
            'followers_count', 'following_count', 'recipes_count', 'is_following',
        ]

    def get_is_following(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return Follow.objects.filter(follower=request.user, following=obj).exists()


class FollowSerializer(serializers.ModelSerializer):
    """Minimal serializer for follower/following list items."""
    bio    = serializers.CharField(source='profile.bio',    read_only=True, default='')
    avatar = serializers.ImageField(source='profile.avatar', read_only=True, default=None)

    class Meta:
        model  = User
        fields = ['id', 'name', 'email', 'bio', 'avatar']


# ── Notifications ─────────────────────────────────────────────────────────────

class NotificationSerializer(serializers.ModelSerializer):
    actor_name   = serializers.CharField(source='actor.name',  read_only=True)
    actor_avatar = serializers.ImageField(source='actor.profile.avatar', read_only=True, default=None)
    recipe_title = serializers.CharField(source='recipe.title', read_only=True, default=None)

    class Meta:
        model  = Notification
        fields = [
            'id', 'kind', 'is_read', 'created_at',
            'actor_name', 'actor_avatar', 'recipe_title', 'recipe',
        ]
        read_only_fields = ['id', 'kind', 'created_at', 'actor_name', 'actor_avatar', 'recipe_title']
