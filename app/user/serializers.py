from django.contrib.auth import get_user_model
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user object"""

    class Meta:
        model = get_user_model()
        fields = ('email', 'password', 'name')
        extra_kwargs = {
            # Password can be sent IN, but never sent OUT
            'password': {
                'write_only': True,
                'min_length': 5
            }
        }

    def create(self, validated_data):
        """
        Create and return a user with encrypted password.

        Express equivalent:
        User.create({
          email,
          password: hash(password),
          name
        })
        """
        return get_user_model().objects.create_user(**validated_data)
