"""Serializers for the user API."""
from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import gettext as _

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user object."""

    class Meta:
        model = get_user_model()
        fields = ('email', 'password', 'name')
        extra_kwargs = {
            'password': {
                'write_only': True,
                'min_length': 5,
            }
        }

    def create(self, validated_data):
        """Create and return a user with an encrypted password."""
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Update and return user, re-hashing password if provided."""
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user


class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the legacy DRF auth token (email + password)."""
    email = serializers.EmailField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False,
    )

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password,
        )
        if not user:
            raise serializers.ValidationError(
                _('Unable to authenticate with provided credentials.'),
                code='authorization',
            )
        attrs['user'] = user
        return attrs


class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    JWT token pair serializer that accepts 'email' instead of 'username'.

    simplejwt defaults to the USERNAME_FIELD on the user model, which we've
    set to 'email', so this works automatically — we just add extra claims.
    """

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Embed non-sensitive user info directly in the token payload
        # so the frontend does not need an extra /me/ call on login.
        token['name'] = user.name
        token['email'] = user.email
        return token
