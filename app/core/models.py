"""
Database models.
This file contains all database models for the project.
"""

# Import Django's base model system
from django.db import models

# Import authentication-related base classes from Django
from django.contrib.auth.models import (
    AbstractBaseUser,   # Provides core authentication features (password, login)
    BaseUserManager,   # Base class for creating custom user managers
    PermissionsMixin,  # Adds permission and group support
)


class UserManager(BaseUserManager):
    """
    Manager for users.
    Handles creating users in a correct and secure way.
    """

    def create_user(self, email, password=None, **extra_field):
        """
        Create, save and return a new user.

        email: user's email address (used for authentication)
        password: raw password (will be hashed)
        extra_field: additional fields like name
        """

        # Create a user instance using the associated User model
        user = self.model(email=self.normalize_email(email), **extra_field)

        # Hash and set the user's password securely
        user.set_password(password)

        # Save the user to the database
        # using=self._db supports multiple databases if configured
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """
    User model for the system.
    Uses email instead of username for authentication.
    """

    # Email field (used as the unique identifier)
    email = models.EmailField(max_length=255, unique=True)

    # User's display name
    name = models.CharField(max_length=255)

    # Determines whether the user account is active
    is_active = models.BooleanField(default=True)

    # Determines whether the user can access Django admin
    is_staff = models.BooleanField(default=False)

    # Attach the custom user manager to this model
    objects = UserManager()

    # Field used for authentication instead of username
    USERNAME_FIELD = 'email'
