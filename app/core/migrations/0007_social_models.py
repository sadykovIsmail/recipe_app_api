"""
Add social models: UserProfile, Follow, RecipeLike, RecipeComment, Notification.
Also adds created_at/updated_at to Recipe and DB indexes.
"""
import core.models
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_recipe_image'),
    ]

    operations = [
        # ── Recipe timestamps & indexes ───────────────────────────────────────
        migrations.AddField(
            model_name='recipe',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='recipe',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddIndex(
            model_name='recipe',
            index=models.Index(fields=['-created_at'], name='core_recipe_created_idx'),
        ),
        migrations.AddIndex(
            model_name='recipe',
            index=models.Index(fields=['user', '-created_at'], name='core_recipe_user_created_idx'),
        ),

        # ── UserProfile ───────────────────────────────────────────────────────
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bio', models.TextField(blank=True, max_length=500)),
                ('avatar', models.ImageField(blank=True, null=True, upload_to=core.models.avatar_file_path)),
                ('website', models.URLField(blank=True)),
                ('location', models.CharField(blank=True, max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.OneToOneField(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='profile',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
        ),

        # ── Follow ────────────────────────────────────────────────────────────
        migrations.CreateModel(
            name='Follow',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('follower', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='following',
                    to=settings.AUTH_USER_MODEL,
                )),
                ('following', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='followers',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
        ),
        migrations.AddConstraint(
            model_name='follow',
            constraint=models.UniqueConstraint(fields=['follower', 'following'], name='unique_follow'),
        ),
        migrations.AddIndex(
            model_name='follow',
            index=models.Index(fields=['follower'], name='core_follow_follower_idx'),
        ),
        migrations.AddIndex(
            model_name='follow',
            index=models.Index(fields=['following'], name='core_follow_following_idx'),
        ),

        # ── RecipeLike ────────────────────────────────────────────────────────
        migrations.CreateModel(
            name='RecipeLike',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='liked_recipes',
                    to=settings.AUTH_USER_MODEL,
                )),
                ('recipe', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='likes',
                    to='core.recipe',
                )),
            ],
        ),
        migrations.AddConstraint(
            model_name='recipelike',
            constraint=models.UniqueConstraint(fields=['user', 'recipe'], name='unique_recipe_like'),
        ),
        migrations.AddIndex(
            model_name='recipelike',
            index=models.Index(fields=['recipe', '-created_at'], name='core_like_recipe_idx'),
        ),
        migrations.AddIndex(
            model_name='recipelike',
            index=models.Index(fields=['user'], name='core_like_user_idx'),
        ),

        # ── RecipeComment ─────────────────────────────────────────────────────
        migrations.CreateModel(
            name='RecipeComment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(max_length=1000)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='comments',
                    to=settings.AUTH_USER_MODEL,
                )),
                ('recipe', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='comments',
                    to='core.recipe',
                )),
            ],
            options={'ordering': ['-created_at']},
        ),
        migrations.AddIndex(
            model_name='recipecomment',
            index=models.Index(fields=['recipe', '-created_at'], name='core_comment_recipe_idx'),
        ),

        # ── Notification ──────────────────────────────────────────────────────
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('kind', models.CharField(
                    choices=[
                        ('new_follower', 'New follower'),
                        ('recipe_like', 'Recipe liked'),
                        ('recipe_comment', 'Recipe commented'),
                    ],
                    max_length=30,
                )),
                ('is_read', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('actor', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='sent_notifications',
                    to=settings.AUTH_USER_MODEL,
                )),
                ('recipient', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='notifications',
                    to=settings.AUTH_USER_MODEL,
                )),
                ('recipe', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='notifications',
                    to='core.recipe',
                )),
            ],
            options={'ordering': ['-created_at']},
        ),
        migrations.AddIndex(
            model_name='notification',
            index=models.Index(
                fields=['recipient', 'is_read', '-created_at'],
                name='core_notif_recipient_idx',
            ),
        ),
    ]
