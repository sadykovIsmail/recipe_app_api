# recipe — Core Business Logic App

[![Python](https://img.shields.io/badge/Python-3.9-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![DRF](https://img.shields.io/badge/Django_REST_Framework-3.12-ff1709?style=flat-square&logo=django&logoColor=white)](https://www.django-rest-framework.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13-316192?style=flat-square&logo=postgresql&logoColor=white)](https://www.postgresql.org/)

The `recipe` app contains the core business logic of the API. It provides full CRUD for recipes and CRUD-minus-create endpoints for tags and ingredients. All resources are user-scoped — users interact only with their own data. Nested serializer patterns handle the many-to-many relationships between recipes, tags, and ingredients in a single API call.

---

## Table of Contents

- [Overview](#overview)
- [Data Flow](#data-flow)
- [Serializers](#serializers)
- [Views](#views)
- [URL Routes](#url-routes)
- [API Endpoints](#api-endpoints)
- [Tests](#tests)

---

## Overview

```
recipe/
├── serializers.py               # Recipe, Tag, Ingredient serializers
├── views.py                     # RecipeViewSet, TagViewSet, IngredientViewSet
├── urls.py                      # DRF Router registration
└── tests/
    ├── test_recipe_api.py       # Recipe endpoint tests
    ├── test_tags_api.py         # Tag endpoint tests
    └── test_ingredients_api.py  # Ingredient endpoint tests
```

---

## Data Flow

```
HTTP Request  (with Authorization: Token ...)
      │
      ▼
URL Router  (/api/recipe/*)
      │
      ▼
TokenAuthentication  ──▶  401 if invalid/missing token
      │
      ▼
ViewSet  (RecipeViewSet / TagViewSet / IngredientViewSet)
      │
      ▼
get_queryset()  ──▶  filters all results to request.user
      │
      ▼
Serializer  (validate, deserialize)
      │
      ├──▶  400 Bad Request on invalid data
      │
      ▼
ORM  (create / update / delete / retrieve)
      │
      ▼
PostgreSQL Database
      │
      ▼
Serializer  (serialize response)
      │
      ▼
JSON Response
```

---

## Serializers

### `IngredientSerializer`

Serializes `core.Ingredient` model instances.

| Field | Type | Access |
|-------|------|--------|
| `id` | integer | read-only |
| `name` | string | read/write |

---

### `TagSerializer`

Serializes `core.Tag` model instances.

| Field | Type | Access |
|-------|------|--------|
| `id` | integer | read-only |
| `name` | string | read/write |

---

### `RecipeSerializer`

Used for the **list** action (`GET /recipes/`). Includes nested tags and ingredients as lightweight embedded objects.

| Field | Type | Access |
|-------|------|--------|
| `id` | integer | read-only |
| `title` | string | read/write |
| `time_minutes` | integer | read/write |
| `price` | decimal | read/write |
| `link` | string | read/write (optional) |
| `tags` | `TagSerializer[]` | read/write, optional |
| `ingredients` | `IngredientSerializer[]` | read/write, optional |

**Custom methods:**

- **`_get_or_create_tags(tags, recipe)`** — iterates the `tags` list. For each entry, calls `Tag.objects.get_or_create(user=user, **tag_data)` to prevent duplicates, then adds to `recipe.tags`.
- **`_get_or_create_ingredients(ingredients, recipe)`** — same pattern for ingredients.
- **`create(validated_data)`** — pops `tags` and `ingredients` before `Recipe.objects.create()`, then delegates to the helpers above.
- **`update(instance, validated_data)`** — pops and clears existing M2M sets, then re-assigns via helpers. All other fields use default `super().update()`.

---

### `RecipeDetailSerializer`

Extends `RecipeSerializer` by adding the `description` field. Used for retrieve, create, and update actions.

| Additional Field | Type | Access |
|-----------------|------|--------|
| `description` | string | read/write (optional) |

---

## Views

### `RecipeViewSet`

```
Class:    ModelViewSet
Auth:     TokenAuthentication + IsAuthenticated
Queryset: Recipe filtered by request.user, ordered by -id
```

| Action | Method | Serializer Used |
|--------|--------|-----------------|
| `list` | GET | `RecipeSerializer` |
| `retrieve` | GET | `RecipeDetailSerializer` |
| `create` | POST | `RecipeDetailSerializer` |
| `update` | PUT | `RecipeDetailSerializer` |
| `partial_update` | PATCH | `RecipeDetailSerializer` |
| `destroy` | DELETE | — |

`get_serializer_class()` returns `RecipeSerializer` for `list`, `RecipeDetailSerializer` for all other actions.

`perform_create(serializer)` calls `serializer.save(user=self.request.user)`, binding the recipe to the authenticated user.

---

### `BaseRecipeAttrViewSet`

Abstract base ViewSet composed from `DestroyModelMixin`, `UpdateModelMixin`, `ListModelMixin`, and `GenericViewSet`. Provides list, update, and delete — but not create or retrieve.

```
Auth:     TokenAuthentication + IsAuthenticated
Queryset: Filtered by request.user, ordered by name ascending
```

---

### `TagViewSet`

Extends `BaseRecipeAttrViewSet`. Manages the authenticated user's tags.

```
Model:    core.Tag
Serializer: TagSerializer
```

---

### `IngredientViewSet`

Extends `BaseRecipeAttrViewSet`. Manages the authenticated user's ingredients.

```
Model:    core.Ingredient
Serializer: IngredientSerializer
```

---

## URL Routes

Registered via DRF `DefaultRouter`, mounted at `/api/recipe/` in the root `urls.py`.

```python
router = DefaultRouter()
router.register('recipes',     views.RecipeViewSet)
router.register('tags',        views.TagViewSet)
router.register('ingredients', views.IngredientViewSet)
```

| URL Pattern | Methods | Action |
|-------------|---------|--------|
| `/api/recipe/recipes/` | GET | List all user's recipes |
| `/api/recipe/recipes/` | POST | Create a recipe |
| `/api/recipe/recipes/{id}/` | GET | Retrieve a recipe |
| `/api/recipe/recipes/{id}/` | PUT | Full update |
| `/api/recipe/recipes/{id}/` | PATCH | Partial update |
| `/api/recipe/recipes/{id}/` | DELETE | Delete |
| `/api/recipe/tags/` | GET | List all user's tags |
| `/api/recipe/tags/{id}/` | PUT / PATCH | Update a tag |
| `/api/recipe/tags/{id}/` | DELETE | Delete a tag |
| `/api/recipe/ingredients/` | GET | List all user's ingredients |
| `/api/recipe/ingredients/{id}/` | PUT / PATCH | Update an ingredient |
| `/api/recipe/ingredients/{id}/` | DELETE | Delete an ingredient |

---

## API Endpoints

### List recipes

```http
GET /api/recipe/recipes/
Authorization: Token <token>
```

**Response `200 OK`:**
```json
[
  {
    "id": 1,
    "title": "Pasta Carbonara",
    "time_minutes": 25,
    "price": "12.50",
    "link": "",
    "tags": [{ "id": 1, "name": "Italian" }],
    "ingredients": [
      { "id": 1, "name": "Spaghetti" },
      { "id": 2, "name": "Eggs" }
    ]
  }
]
```

---

### Create a recipe with nested tags and ingredients

```http
POST /api/recipe/recipes/
Authorization: Token <token>
Content-Type: application/json

{
  "title": "Chicken Tikka Masala",
  "time_minutes": 45,
  "price": "18.00",
  "description": "Rich, creamy tomato curry.",
  "tags": [
    { "name": "Indian" },
    { "name": "Curry" }
  ],
  "ingredients": [
    { "name": "Chicken" },
    { "name": "Tomatoes" },
    { "name": "Heavy Cream" }
  ]
}
```

> If `"Indian"` already exists in your tag list, the API reuses it instead of creating a duplicate.

**Response `201 Created`:**
```json
{
  "id": 3,
  "title": "Chicken Tikka Masala",
  "time_minutes": 45,
  "price": "18.00",
  "description": "Rich, creamy tomato curry.",
  "link": "",
  "tags": [
    { "id": 2, "name": "Indian" },
    { "id": 3, "name": "Curry" }
  ],
  "ingredients": [
    { "id": 5, "name": "Chicken" },
    { "id": 6, "name": "Tomatoes" },
    { "id": 7, "name": "Heavy Cream" }
  ]
}
```

---

### Partial update

```http
PATCH /api/recipe/recipes/3/
Authorization: Token <token>
Content-Type: application/json

{
  "time_minutes": 50,
  "tags": [{ "name": "Indian" }]
}
```

---

### Delete

```http
DELETE /api/recipe/recipes/3/
Authorization: Token <token>
```

**Response `204 No Content`**

---

### Update a tag

```http
PATCH /api/recipe/tags/2/
Authorization: Token <token>
Content-Type: application/json

{ "name": "South Asian" }
```

---

### Delete an ingredient

```http
DELETE /api/recipe/ingredients/5/
Authorization: Token <token>
```

---

## Tests

Run with `python manage.py test recipe`.

### `test_recipe_api.py`

**`PublicRecipeAPITests`**

| Test | Description |
|------|-------------|
| `test_auth_required` | Unauthenticated request returns `401` |

**`PrivateRecipeApiTests`**

| Test | Description |
|------|-------------|
| `test_retrieve_recipes` | Returns list of user's recipes |
| `test_recipe_list_limited_to_user` | Other users' recipes not included |
| `test_get_recipe_detail` | Returns full recipe detail with description |
| `test_create_recipe` | Recipe created and returned with `201` |
| `test_partial_update` | PATCH updates specified fields only |
| `test_full_update` | PUT replaces entire recipe |
| `test_update_user_returns_error` | Cannot reassign recipe to another user |
| `test_delete_recipe` | Recipe deleted, returns `204` |
| `test_recipe_other_users_recipe_error` | Cannot delete another user's recipe |
| `test_create_recipe_with_new_tags` | Tags created inline with recipe |
| `test_create_recipe_with_existing_tags` | Existing tag reused (no duplicate) |
| `test_create_tag_on_update` | New tag added via PATCH |
| `test_update_recipe_assign_tag` | Existing tag assigned via PATCH |
| `test_clear_recipe_tags` | All tags removed by patching with `[]` |
| `test_create_recipe_with_new_ingredient` | Ingredients created inline |
| `test_create_recipe_with_existing_ingredient` | Existing ingredient reused |
| `test_create_ingredient_on_update` | New ingredient added via PATCH |
| `test_update_recipe_assign_ingredient` | Existing ingredient assigned via PATCH |
| `test_clear_recipe_ingredients` | All ingredients removed by patching with `[]` |

---

### `test_tags_api.py`

| Test | Description |
|------|-------------|
| `test_auth_required` | Unauthenticated request returns `401` |
| `test_retrieve_tags` | Returns list of user's tags |
| `test_tags_limited_to_user` | Other users' tags not included |
| `test_update_tag` | PATCH updates tag name |
| `test_delete_tag` | Tag deleted, returns `204` |

---

### `test_ingredients_api.py`

| Test | Description |
|------|-------------|
| `test_auth_required` | Unauthenticated request returns `401` |
| `test_retrieve_ingredients` | Returns list of user's ingredients |
| `test_ingredients_limited_to_user` | Other users' ingredients not included |
| `test_update_ingredient` | PATCH updates ingredient name |
| `test_delete_ingredient` | Ingredient deleted, returns `204` |
