"""
Database models.
"""
import os
import uuid

from django.conf import settings
from django.db import models
from django.db.models import UniqueConstraint


# ── Helpers ───────────────────────────────────────────────────────────────────

def recipe_image_file_path(instance, filename):
    """Generate a unique file path for a recipe image."""
    ext = os.path.splitext(filename)[1]
    return os.path.join('uploads', 'recipe', f'{uuid.uuid4()}{ext}')


def avatar_file_path(instance, filename):
    """Generate a unique file path for a user avatar."""
    ext = os.path.splitext(filename)[1]
    return os.path.join('uploads', 'avatar', f'{uuid.uuid4()}{ext}')


# ── User ──────────────────────────────────────────────────────────────────────

from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_field):
        if not email:
            raise ValueError('User must have an email address')
        user = self.model(email=self.normalize_email(email), **extra_field)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model — email as primary identifier."""
    email    = models.EmailField(max_length=255, unique=True)
    name     = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff  = models.BooleanField(default=False)

    objects = UserManager()
    USERNAME_FIELD = 'email'


class UserProfile(models.Model):
    """Extended public profile for a user (one-to-one)."""
    user     = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile'
    )
    bio      = models.TextField(blank=True, max_length=500)
    avatar   = models.ImageField(null=True, blank=True, upload_to=avatar_file_path)
    website  = models.URLField(blank=True)
    location = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.email} profile'

    @property
    def followers_count(self):
        return self.user.followers.count()

    @property
    def following_count(self):
        return self.user.following.count()

    @property
    def recipes_count(self):
        return self.user.recipe_set.count()


# ── Social graph ──────────────────────────────────────────────────────────────

class Follow(models.Model):
    """Directed follow relationship: follower → following."""
    follower  = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='following',   # request.user.following.all() = who I follow
    )
    following = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='followers',   # user.followers.all() = who follows them
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            UniqueConstraint(fields=['follower', 'following'], name='unique_follow'),
        ]
        indexes = [
            models.Index(fields=['follower']),
            models.Index(fields=['following']),
        ]

    def __str__(self):
        return f'{self.follower.email} → {self.following.email}'


# ── Recipe ────────────────────────────────────────────────────────────────────

class Recipe(models.Model):
    """Recipe object."""
    user         = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title        = models.CharField(max_length=255)
    description  = models.TextField(blank=True)
    time_minutes = models.IntegerField()
    price        = models.DecimalField(max_digits=5, decimal_places=2)
    link         = models.CharField(max_length=255, blank=True)
    tags         = models.ManyToManyField('Tag')
    ingredients  = models.ManyToManyField('Ingredient')
    image        = models.ImageField(null=True, blank=True, upload_to=recipe_image_file_path)
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['user', '-created_at']),
        ]

    def __str__(self):
        return self.title


class Tag(models.Model):
    """Tag for filtering recipes."""
    name = models.CharField(max_length=255)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Ingredient for recipes."""
    name = models.CharField(max_length=255)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


# ── Recipe interactions ───────────────────────────────────────────────────────

class RecipeLike(models.Model):
    """A user liking a recipe (toggle)."""
    user   = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='liked_recipes'
    )
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            UniqueConstraint(fields=['user', 'recipe'], name='unique_recipe_like'),
        ]
        indexes = [
            models.Index(fields=['recipe', '-created_at']),
            models.Index(fields=['user']),
        ]


class RecipeComment(models.Model):
    """A user commenting on a recipe."""
    user       = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments'
    )
    recipe     = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='comments')
    text       = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['recipe', '-created_at']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.email}: {self.text[:50]}'


# ── Notifications ─────────────────────────────────────────────────────────────

class Notification(models.Model):
    """In-app notification for social events."""

    class Kind(models.TextChoices):
        NEW_FOLLOWER  = 'new_follower',  'New follower'
        RECIPE_LIKE   = 'recipe_like',   'Recipe liked'
        RECIPE_COMMENT = 'recipe_comment', 'Recipe commented'

    recipient  = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications'
    )
    actor      = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_notifications'
    )
    kind       = models.CharField(max_length=30, choices=Kind.choices)
    recipe     = models.ForeignKey(
        Recipe, null=True, blank=True, on_delete=models.CASCADE, related_name='notifications'
    )
    is_read    = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes  = [
            models.Index(fields=['recipient', 'is_read', '-created_at']),
        ]

    def __str__(self):
        return f'{self.kind} → {self.recipient.email}'
