"""Tests for the recipe API."""
import os
import tempfile
from decimal import Decimal

from PIL import Image

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe, Tag, Ingredient
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer


RECIPES_URL = reverse('recipe:recipe-list')


def detail_url(recipe_id):
    return reverse('recipe:recipe-detail', args=[recipe_id])


def image_upload_url(recipe_id):
    return reverse('recipe:recipe-upload-image', args=[recipe_id])


def create_recipe(user, **params):
    defaults = {
        'title': 'Sample recipe title',
        'time_minutes': 22,
        'price': Decimal('5.25'),
        'description': 'Sample description',
        'link': 'http://example.com/recipe.pdf',
    }
    defaults.update(params)
    return Recipe.objects.create(user=user, **defaults)


def create_user(**params):
    return get_user_model().objects.create_user(**params)


# ── Public (unauthenticated) ──────────────────────────────────────────────────

class PublicRecipeAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(RECIPES_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


# ── Private (authenticated) ───────────────────────────────────────────────────

class PrivateRecipeApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = create_user(email='user@example.com', password='test123')
        self.client.force_authenticate(self.user)

    # -- List -----------------------------------------------------------------

    def test_retrieve_recipes(self):
        create_recipe(user=self.user)
        create_recipe(user=self.user)
        res = self.client.get(RECIPES_URL)
        recipes = Recipe.objects.filter(user=self.user).order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # Response is paginated: results live under 'results' key
        self.assertEqual(res.data['results'], serializer.data)

    def test_recipe_list_limited_to_user(self):
        other_user = create_user(email='other@example.com', password='password123')
        create_recipe(user=other_user)
        create_recipe(user=self.user)
        res = self.client.get(RECIPES_URL)
        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['results'], serializer.data)

    # -- Detail ---------------------------------------------------------------

    def test_get_recipe_detail(self):
        recipe = create_recipe(user=self.user)
        res = self.client.get(detail_url(recipe.id))
        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)

    # -- Create ---------------------------------------------------------------

    def test_create_recipe(self):
        payload = {'title': 'Sample recipe', 'time_minutes': 30, 'price': Decimal('5.9')}
        res = self.client.post(RECIPES_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)
        self.assertEqual(recipe.user, self.user)

    # -- Update ---------------------------------------------------------------

    def test_partial_update(self):
        original_link = 'https://example.com/recipe.pdf'
        recipe = create_recipe(user=self.user, title='Sample recipe title', link=original_link)
        res = self.client.patch(detail_url(recipe.id), {'title': 'New recipe title'})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        self.assertEqual(recipe.title, 'New recipe title')
        self.assertEqual(recipe.link, original_link)

    def test_full_update(self):
        recipe = create_recipe(user=self.user)
        payload = {
            'title': 'New recipe title',
            'link': 'https://example.com/new-recipe.pdf',
            'description': 'New recipe description',
            'time_minutes': 10,
            'price': Decimal('2.50'),
        }
        res = self.client.put(detail_url(recipe.id), payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)

    def test_update_user_is_ignored(self):
        """Passing a different user ID in the payload must not change recipe owner."""
        new_user = create_user(email='user2@example.com', password='test123')
        recipe = create_recipe(user=self.user)
        self.client.patch(detail_url(recipe.id), {'user': new_user.id})
        recipe.refresh_from_db()
        self.assertEqual(recipe.user, self.user)

    # -- Delete ---------------------------------------------------------------

    def test_delete_recipe(self):
        recipe = create_recipe(user=self.user)
        res = self.client.delete(detail_url(recipe.id))
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Recipe.objects.filter(id=recipe.id).exists())

    def test_delete_other_users_recipe_returns_404(self):
        other_user = create_user(email='user2@example.com', password='test123')
        recipe = create_recipe(user=other_user)
        res = self.client.delete(detail_url(recipe.id))
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Recipe.objects.filter(id=recipe.id).exists())

    # -- Tags -----------------------------------------------------------------

    def test_create_recipe_with_new_tags(self):
        payload = {
            'title': 'Thai Prawn Curry',
            'time_minutes': 30,
            'price': Decimal('2.50'),
            'tags': [{'name': 'Thai'}, {'name': 'Dinner'}],
        }
        res = self.client.post(RECIPES_URL, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        self.assertEqual(recipe.tags.count(), 2)

    def test_create_recipe_with_existing_tags(self):
        tag_indian = Tag.objects.create(user=self.user, name='Indian')
        payload = {
            'title': 'Pongal',
            'time_minutes': 60,
            'price': Decimal('4.50'),
            'tags': [{'name': 'Indian'}, {'name': 'Breakfast'}],
        }
        res = self.client.post(RECIPES_URL, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        self.assertEqual(recipe.tags.count(), 2)
        self.assertIn(tag_indian, recipe.tags.all())

    def test_create_tag_on_update(self):
        recipe = create_recipe(user=self.user)
        res = self.client.patch(detail_url(recipe.id), {'tags': [{'name': 'Lunch'}]}, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        new_tag = Tag.objects.get(user=self.user, name='Lunch')
        self.assertIn(new_tag, recipe.tags.all())

    def test_update_recipe_assign_tag(self):
        tag_breakfast = Tag.objects.create(user=self.user, name='Breakfast')
        recipe = create_recipe(user=self.user)
        recipe.tags.add(tag_breakfast)
        tag_lunch = Tag.objects.create(user=self.user, name='Lunch')
        res = self.client.patch(detail_url(recipe.id), {'tags': [{'name': 'Lunch'}]}, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(tag_lunch, recipe.tags.all())
        self.assertNotIn(tag_breakfast, recipe.tags.all())

    def test_clear_recipe_tags(self):
        tag = Tag.objects.create(user=self.user, name='Dessert')
        recipe = create_recipe(user=self.user)
        recipe.tags.add(tag)
        res = self.client.patch(detail_url(recipe.id), {'tags': []}, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.tags.count(), 0)

    # -- Ingredients ----------------------------------------------------------

    def test_create_recipe_with_new_ingredients(self):
        payload = {
            'title': 'Cauliflower Tacos',
            'time_minutes': 60,
            'price': Decimal('4.30'),
            'ingredients': [{'name': 'Cauliflower'}, {'name': 'Salt'}],
        }
        res = self.client.post(RECIPES_URL, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        self.assertEqual(recipe.ingredients.count(), 2)

    def test_create_recipe_with_existing_ingredient(self):
        ingredient = Ingredient.objects.create(user=self.user, name='Lemon')
        payload = {
            'title': 'Vietnamese Soup',
            'time_minutes': 25,
            'price': '2.55',
            'ingredients': [{'name': 'Lemon'}, {'name': 'Fish Sauce'}],
        }
        res = self.client.post(RECIPES_URL, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        self.assertEqual(recipe.ingredients.count(), 2)
        self.assertIn(ingredient, recipe.ingredients.all())

    def test_create_ingredient_on_update(self):
        recipe = create_recipe(user=self.user)
        res = self.client.patch(
            detail_url(recipe.id), {'ingredients': [{'name': 'Limes'}]}, format='json'
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        new_ing = Ingredient.objects.get(user=self.user, name='Limes')
        self.assertIn(new_ing, recipe.ingredients.all())

    def test_update_recipe_assign_ingredient(self):
        ing1 = Ingredient.objects.create(user=self.user, name='Pepper')
        recipe = create_recipe(user=self.user)
        recipe.ingredients.add(ing1)
        ing2 = Ingredient.objects.create(user=self.user, name='Chilli')
        res = self.client.patch(
            detail_url(recipe.id), {'ingredients': [{'name': 'Chilli'}]}, format='json'
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(ing2, recipe.ingredients.all())
        self.assertNotIn(ing1, recipe.ingredients.all())

    def test_clear_recipe_ingredients(self):
        ingredient = Ingredient.objects.create(user=self.user, name='Garlic')
        recipe = create_recipe(user=self.user)
        recipe.ingredients.add(ingredient)
        res = self.client.patch(detail_url(recipe.id), {'ingredients': []}, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.ingredients.count(), 0)

    # -- Filtering ------------------------------------------------------------

    def test_filter_recipes_by_tags(self):
        """Recipes can be filtered by tag ID."""
        r1 = create_recipe(user=self.user, title='Thai Curry')
        r2 = create_recipe(user=self.user, title='Aubergine')
        tag1 = Tag.objects.create(user=self.user, name='Vegan')
        r1.tags.add(tag1)
        create_recipe(user=self.user, title='Fish and Chips')

        res = self.client.get(RECIPES_URL, {'tags': f'{tag1.id}'})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        ids = [r['id'] for r in res.data['results']]
        self.assertIn(r1.id, ids)
        self.assertNotIn(r2.id, ids)

    def test_filter_recipes_by_ingredients(self):
        """Recipes can be filtered by ingredient ID."""
        r1 = create_recipe(user=self.user, title='Posh Beans on Toast')
        r2 = create_recipe(user=self.user, title='Chicken Cacciatore')
        ing = Ingredient.objects.create(user=self.user, name='Beans')
        r1.ingredients.add(ing)
        create_recipe(user=self.user, title='Red Lentil Daal')

        res = self.client.get(RECIPES_URL, {'ingredients': f'{ing.id}'})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        ids = [r['id'] for r in res.data['results']]
        self.assertIn(r1.id, ids)
        self.assertNotIn(r2.id, ids)

    def test_search_recipes_by_title(self):
        """Recipes can be searched by title."""
        create_recipe(user=self.user, title='Chocolate Cake')
        create_recipe(user=self.user, title='Vanilla Ice Cream')

        res = self.client.get(RECIPES_URL, {'search': 'chocolate'})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        titles = [r['title'] for r in res.data['results']]
        self.assertIn('Chocolate Cake', titles)
        self.assertNotIn('Vanilla Ice Cream', titles)


# ── Image upload ──────────────────────────────────────────────────────────────

class RecipeImageUploadTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = create_user(email='user@example.com', password='test123')
        self.client.force_authenticate(self.user)
        self.recipe = create_recipe(user=self.user)

    def tearDown(self):
        self.recipe.image.delete()

    def test_upload_image(self):
        """Uploading a valid image returns 200 and image URL."""
        url = image_upload_url(self.recipe.id)
        with tempfile.NamedTemporaryFile(suffix='.jpg') as image_file:
            img = Image.new('RGB', (10, 10))
            img.save(image_file, format='JPEG')
            image_file.seek(0)
            payload = {'image': image_file}
            res = self.client.post(url, payload, format='multipart')

        self.recipe.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('image', res.data)
        self.assertTrue(os.path.exists(self.recipe.image.path))

    def test_upload_image_bad_request(self):
        """Uploading a non-image file returns 400."""
        url = image_upload_url(self.recipe.id)
        payload = {'image': 'not-an-image'}
        res = self.client.post(url, payload, format='multipart')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
