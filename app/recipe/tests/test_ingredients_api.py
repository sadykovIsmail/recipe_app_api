"""Tests for the ingredients API."""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient, Recipe
from recipe.serializers import IngredientSerializer


INGREDIENTS_URL = reverse('recipe:ingredient-list')


def detail_url(ingredient_id):
    return reverse('recipe:ingredient-detail', args=[ingredient_id])


def create_user(email='user@example.com', password='testpass123'):
    return get_user_model().objects.create_user(email=email, password=password)


class PublicIngredientsApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(INGREDIENTS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientApiTests(TestCase):
    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredients(self):
        Ingredient.objects.create(user=self.user, name='Kale')
        Ingredient.objects.create(user=self.user, name='Vanilla')
        res = self.client.get(INGREDIENTS_URL)
        ingredients = Ingredient.objects.filter(user=self.user).order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # Paginated
        self.assertEqual(res.data['results'], serializer.data)

    def test_ingredients_limited_to_user(self):
        user2 = create_user(email='other@example.com')
        Ingredient.objects.create(user=user2, name='Salt')
        ing = Ingredient.objects.create(user=self.user, name='Pepper')
        res = self.client.get(INGREDIENTS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data['results']), 1)
        self.assertEqual(res.data['results'][0]['name'], ing.name)

    def test_update_ingredient(self):
        ingredient = Ingredient.objects.create(user=self.user, name='Cilantro')
        res = self.client.patch(detail_url(ingredient.id), {'name': 'Coriander'})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        ingredient.refresh_from_db()
        self.assertEqual(ingredient.name, 'Coriander')

    def test_delete_ingredient(self):
        ingredient = Ingredient.objects.create(user=self.user, name='Lettuce')
        res = self.client.delete(detail_url(ingredient.id))
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Ingredient.objects.filter(id=ingredient.id).exists())

    def test_filter_ingredients_assigned_only(self):
        """assigned_only=1 returns only ingredients linked to a recipe."""
        ing1 = Ingredient.objects.create(user=self.user, name='Apples')
        ing2 = Ingredient.objects.create(user=self.user, name='Turkey')
        recipe = Recipe.objects.create(
            user=self.user, title='Apple Crumble', time_minutes=20, price=Decimal('3.00')
        )
        recipe.ingredients.add(ing1)

        res = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})
        s1 = IngredientSerializer(ing1)
        s2 = IngredientSerializer(ing2)
        self.assertIn(s1.data, res.data['results'])
        self.assertNotIn(s2.data, res.data['results'])

    def test_search_ingredients_by_name(self):
        Ingredient.objects.create(user=self.user, name='Garlic')
        Ingredient.objects.create(user=self.user, name='Ginger')
        res = self.client.get(INGREDIENTS_URL, {'search': 'garlic'})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        names = [i['name'] for i in res.data['results']]
        self.assertIn('Garlic', names)
        self.assertNotIn('Ginger', names)
