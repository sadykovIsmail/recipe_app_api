"""Tests for the tags API."""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag, Recipe
from recipe.serializers import TagSerializer


TAGS_URL = reverse('recipe:tag-list')


def detail_url(tag_id):
    return reverse('recipe:tag-detail', args=[tag_id])


def create_user(email='user@example.com', password='testpass123'):
    return get_user_model().objects.create_user(email=email, password=password)


class PublicTagsApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(TAGS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTests(TestCase):
    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        Tag.objects.create(user=self.user, name='Vegan')
        Tag.objects.create(user=self.user, name='Dessert')
        res = self.client.get(TAGS_URL)
        tags = Tag.objects.filter(user=self.user).order_by('-name')
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # Paginated response
        self.assertEqual(res.data['results'], serializer.data)

    def test_tags_limited_to_user(self):
        user2 = create_user(email='user2@example.com')
        Tag.objects.create(user=user2, name='Fruity')
        tag = Tag.objects.create(user=self.user, name='Comfort Food')
        res = self.client.get(TAGS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data['results']), 1)
        self.assertEqual(res.data['results'][0]['name'], tag.name)
        self.assertEqual(res.data['results'][0]['id'], tag.id)

    def test_update_tag(self):
        tag = Tag.objects.create(user=self.user, name='After Dinner')
        res = self.client.patch(detail_url(tag.id), {'name': 'Dessert'})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tag.refresh_from_db()
        self.assertEqual(tag.name, 'Dessert')

    def test_delete_tag(self):
        tag = Tag.objects.create(user=self.user, name='Breakfast')
        res = self.client.delete(detail_url(tag.id))
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Tag.objects.filter(user=self.user).exists())

    def test_filter_tags_assigned_only(self):
        """assigned_only=1 returns only tags linked to a recipe."""
        tag1 = Tag.objects.create(user=self.user, name='Breakfast')
        tag2 = Tag.objects.create(user=self.user, name='Lunch')
        recipe = Recipe.objects.create(
            user=self.user, title='Pancakes', time_minutes=5, price=Decimal('1.00')
        )
        recipe.tags.add(tag1)

        res = self.client.get(TAGS_URL, {'assigned_only': 1})
        s1 = TagSerializer(tag1)
        s2 = TagSerializer(tag2)
        self.assertIn(s1.data, res.data['results'])
        self.assertNotIn(s2.data, res.data['results'])

    def test_search_tags_by_name(self):
        Tag.objects.create(user=self.user, name='Italian')
        Tag.objects.create(user=self.user, name='Mexican')
        res = self.client.get(TAGS_URL, {'search': 'ital'})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        names = [t['name'] for t in res.data['results']]
        self.assertIn('Italian', names)
        self.assertNotIn('Mexican', names)
