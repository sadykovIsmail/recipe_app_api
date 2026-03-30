"""Celery tasks for the recipe app."""
from celery import shared_task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=10)
def resize_recipe_image(self, recipe_id: int, max_size: int = 800):
    """
    Resize a recipe image to max_size × max_size after upload.
    Runs asynchronously so the API response is instant.
    """
    try:
        from core.models import Recipe
        from PIL import Image as PillowImage
        import io, os
        from django.core.files.base import ContentFile

        recipe = Recipe.objects.get(pk=recipe_id)
        if not recipe.image:
            return

        img = PillowImage.open(recipe.image)
        if img.width > max_size or img.height > max_size:
            img.thumbnail((max_size, max_size), PillowImage.LANCZOS)
            img_io = io.BytesIO()
            fmt = img.format or 'JPEG'
            img.save(img_io, format=fmt, quality=85, optimize=True)
            img_io.seek(0)
            filename = os.path.basename(recipe.image.name)
            recipe.image.save(filename, ContentFile(img_io.read()), save=True)
            logger.info('Resized recipe %s image to %sx%s', recipe_id, max_size, max_size)
    except Exception as exc:
        logger.error('resize_recipe_image failed for recipe %s: %s', recipe_id, exc)
        raise self.retry(exc=exc)


@shared_task
def recompute_trending():
    """
    Recompute the trending recipe list and cache it in Redis.
    Scheduled every 5 minutes via django-celery-beat.
    """
    from datetime import timedelta
    from django.utils import timezone
    from django.core.cache import cache
    from django.db.models import Count
    from core.models import Recipe

    since = timezone.now() - timedelta(days=7)
    trending_ids = list(
        Recipe.objects
        .filter(created_at__gte=since)
        .annotate(likes_count=Count('likes'))
        .order_by('-likes_count', '-created_at')
        .values_list('id', flat=True)[:50]
    )
    cache.set('trending_recipe_ids', trending_ids, timeout=300)
    logger.info('Recomputed trending: %d recipes', len(trending_ids))
    return trending_ids
