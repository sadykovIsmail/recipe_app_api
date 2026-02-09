"""Tests for the ingredients API."""

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient
from recipe.serializers import IngredientSerializer


INGREDIENTS_URL = reverse('recipe:ingredient-list')

def create_user(email='user@example.com', password='testpass123'):
    return get_user_model().objects.create_user(email=email, password=password)

class PublicIngredientsApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required for retrieving ingredients."""
        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientApiTests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_rerieve_ingredients(self):
        """Test retrieving a list of ingredients"""
        Ingredient.objects.create(user=self.user, name='Kale')
        Ingredient.objects.create(user=self.user, name='Vanilla')

        res = self.client.get(INGREDIENTS_URL)

        Ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(Ingredients, many=True)

