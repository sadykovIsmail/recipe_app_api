"""
Database models.
This file contains all database models for the project.
"""
import os
import uuid

from django.conf import settings
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
        if not email:
            raise ValueError('User must have an email address')

        # Create a user instance using the associated User model
        user = self.model(email=self.normalize_email(email), **extra_field)

        # Hash and set the user's password securely
        user.set_password(password)

        # Save the user to the database
        # using=self._db supports multiple databases if configured
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """Create and return a new superuser"""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
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

    objects = UserManager()
    USERNAME_FIELD = 'email'


def recipe_image_file_path(instance, filename):
    """Generate a unique file path for a recipe image."""
    ext = os.path.splitext(filename)[1]
    filename = f'{uuid.uuid4()}{ext}'
    return os.path.join('uploads', 'recipe', filename)


class Recipe(models.Model):
    """Recipe object."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    time_minutes = models.IntegerField()
    price = models.DecimalField(max_digits=5, decimal_places=2)
    link = models.CharField(max_length=255, blank=True)
    tags = models.ManyToManyField('Tag')
    ingredients = models.ManyToManyField('Ingredient')
    image = models.ImageField(null=True, upload_to=recipe_image_file_path)

    def __str__(self):
        return self.title

class Tag(models.Model):
    """Tag for filtering recipes."""
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.name

class Ingredient(models.Model):
    """Ingredient for recipes."""
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.name