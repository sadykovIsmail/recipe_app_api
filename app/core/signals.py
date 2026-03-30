"""
Django signals for the core app.

- Auto-create UserProfile on new User creation
- Fire Notification records on social events (Follow, Like, Comment)
"""
from django.db.models.signals import post_save
from django.dispatch import receiver

from core.models import User, UserProfile, Follow, RecipeLike, RecipeComment, Notification


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create a UserProfile automatically when a new User is registered."""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=Follow)
def notify_new_follower(sender, instance, created, **kwargs):
    """Notify a user when someone follows them."""
    if created and instance.follower != instance.following:
        Notification.objects.create(
            recipient=instance.following,
            actor=instance.follower,
            kind=Notification.Kind.NEW_FOLLOWER,
        )


@receiver(post_save, sender=RecipeLike)
def notify_recipe_liked(sender, instance, created, **kwargs):
    """Notify a recipe author when their recipe is liked."""
    if created and instance.user != instance.recipe.user:
        Notification.objects.create(
            recipient=instance.recipe.user,
            actor=instance.user,
            kind=Notification.Kind.RECIPE_LIKE,
            recipe=instance.recipe,
        )


@receiver(post_save, sender=RecipeComment)
def notify_recipe_commented(sender, instance, created, **kwargs):
    """Notify a recipe author when someone leaves a comment."""
    if created and instance.user != instance.recipe.user:
        Notification.objects.create(
            recipient=instance.recipe.user,
            actor=instance.user,
            kind=Notification.Kind.RECIPE_COMMENT,
            recipe=instance.recipe,
        )
