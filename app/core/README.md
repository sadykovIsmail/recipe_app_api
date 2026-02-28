# core — Foundation App

[![Python](https://img.shields.io/badge/Python-3.9-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-3.2-092E20?style=flat-square&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13-316192?style=flat-square&logo=postgresql&logoColor=white)](https://www.postgresql.org/)

The `core` app is the shared foundation of the project. It owns all database models, the custom user authentication system, Django admin configuration, and the `wait_for_db` startup management command. No business logic lives here — only the data layer and infrastructure concerns shared by every other app.

---

## Table of Contents

- [Overview](#overview)
- [Data Flow](#data-flow)
- [Models](#models)
- [Admin](#admin)
- [Management Commands](#management-commands)
- [Migrations](#migrations)
- [Tests](#tests)

---

## Overview

```
core/
├── models.py                        # All database models
├── admin.py                         # Django admin customizations
├── apps.py                          # App configuration
├── migrations/                      # Database migration history
│   ├── 0001_initial.py              # User model
│   ├── 0002_recipe.py               # Recipe model
│   ├── 0003_auto_20260209_0418.py   # Tag + Ingredient models
│   └── 0004_auto_20260209_2116.py   # M2M relationship refinements
└── management/
    └── commands/
        └── wait_for_db.py           # DB readiness health check
tests/
├── test_models.py                   # Model unit tests
├── test_admin.py                    # Admin view tests
└── test_commands.py                 # Management command tests
```

---

## Data Flow

```
Request arrives at any view
         │
         ▼
  ORM Query (models.py)
         │
         ▼
  PostgreSQL Database
         │
         ▼
  Python model instance
         │
         ▼
  Passed to serializer (user/ or recipe/ apps)
```

---

## Models

### `UserManager`

Custom manager replacing Django's default `BaseUserManager`. Provides two factory methods:

| Method | Description |
|--------|-------------|
| `create_user(email, password, **extra_fields)` | Creates and saves a regular user. Normalizes email, hashes password. |
| `create_superuser(email, password)` | Creates a superuser with `is_staff=True`, `is_active=True`. |

Email is required and validated — passing an empty string raises `ValueError`.

---

### `User`

Custom user model extending `AbstractBaseUser` and `PermissionsMixin`. Replaces Django's default `User` entirely via `AUTH_USER_MODEL = 'core.User'`.

| Field | Type | Description |
|-------|------|-------------|
| `email` | `EmailField(unique=True, max_length=255)` | Primary identifier for authentication |
| `name` | `CharField(max_length=255)` | Display name |
| `is_active` | `BooleanField(default=True)` | Controls login access |
| `is_staff` | `BooleanField(default=False)` | Controls admin access |

**Key settings:**
- `USERNAME_FIELD = 'email'` — email used for `authenticate()` calls
- `objects = UserManager()` — wired to the custom manager above

---

### `Recipe`

Central business entity. Belongs to a `User` and has many-to-many relationships with `Tag` and `Ingredient`.

| Field | Type | Description |
|-------|------|-------------|
| `user` | `ForeignKey(User, CASCADE)` | Owner of the recipe |
| `title` | `CharField(max_length=255)` | Recipe name |
| `description` | `TextField(blank=True)` | Optional detailed description |
| `time_minutes` | `IntegerField` | Estimated cooking time |
| `price` | `DecimalField(max_digits=5, decimal_places=2)` | Estimated cost |
| `link` | `CharField(max_length=255, blank=True)` | Optional external URL |
| `tags` | `ManyToManyField(Tag)` | Associated tags |
| `ingredients` | `ManyToManyField(Ingredient)` | Associated ingredients |

Deleting a user cascades and removes all their recipes.

---

### `Tag`

A label for categorizing recipes. User-scoped: each user maintains their own tag list.

| Field | Type | Description |
|-------|------|-------------|
| `name` | `CharField(max_length=255)` | Tag label |
| `user` | `ForeignKey(User, CASCADE)` | Owner |

---

### `Ingredient`

A named ingredient that can be attached to recipes. User-scoped.

| Field | Type | Description |
|-------|------|-------------|
| `name` | `CharField(max_length=255)` | Ingredient name |
| `user` | `ForeignKey(User, CASCADE)` | Owner |

---

### Entity-Relationship Diagram

```
┌──────────────────────┐
│         User         │
│──────────────────────│
│ id (PK)              │
│ email (unique)       │
│ name                 │
│ is_active            │
│ is_staff             │
└──────┬───────────────┘
       │  1
       │
  ─────┼──────────────────────────────────────────────
  │    │                  │                  │
  │  N │                N │                N │
  │    ▼                  ▼                  ▼
  │ ┌──────────┐    ┌──────────┐    ┌──────────────┐
  │ │  Recipe  │    │   Tag    │    │  Ingredient  │
  │ │──────────│    │──────────│    │──────────────│
  │ │ id (PK)  │    │ id (PK)  │    │ id (PK)      │
  │ │ title    │    │ name     │    │ name         │
  │ │ desc.    │    │ user_id  │    │ user_id      │
  │ │ price    │    └──────────┘    └──────────────┘
  │ │ time_min │       ▲                   ▲
  │ │ link     │       │  M:N              │  M:N
  │ │ user_id  │───────┘                   │
  │ └──────────┘───────────────────────────┘
  └─────────────────────────────────────────
```

---

## Admin

`admin.py` registers all models with Django's admin site and customizes the `User` admin:

```
UserAdmin
  ├── ordering       → [id]
  ├── list_display   → [email, name]
  ├── fieldsets      → Personal Info (email, name) + Permissions (is_active, is_staff)
  └── readonly_fields → [last_login]
```

Also registered with default admin: `Recipe`, `Tag`, `Ingredient`.

---

## Management Commands

### `wait_for_db`

Located at `management/commands/wait_for_db.py`.

**Purpose:** Prevents the Django app from starting before PostgreSQL is ready to accept connections. This is essential in Docker Compose where the database container may still be initializing when the app container starts.

**Behavior:**
1. Attempts `connections['default'].ensure_connection()`
2. On `psycopg2.OperationalError` or Django `OperationalError` — sleeps 1 second and retries
3. Logs readiness status to stdout
4. Succeeds silently when connection is established

**Usage in `docker-compose.yml`:**
```yaml
command: >
  sh -c "python manage.py wait_for_db &&
         python manage.py migrate &&
         python manage.py runserver 0.0.0.0:8000"
```

---

## Migrations

| Migration | Description |
|-----------|-------------|
| `0001_initial` | Creates the custom `User` model with email-based auth |
| `0002_recipe` | Creates the `Recipe` model with FK to `User` |
| `0003_auto_*` | Creates `Tag` and `Ingredient` models |
| `0004_auto_*` | Adds M2M relationships: `Recipe.tags`, `Recipe.ingredients` |

---

## Tests

All tests are in `tests/` and run with `python manage.py test core`.

### `test_models.py`

| Test | Description |
|------|-------------|
| `test_create_user_with_email_successful` | User created with correct email/password |
| `test_new_user_email_normalized` | Email domain is lowercased |
| `test_new_user_without_email_raises_error` | Empty email raises `ValueError` |
| `test_create_superuser` | Superuser has `is_staff=True`, `is_superuser=True` |
| `test_create_recipe` | Recipe created and linked to user |
| `test_create_tag` | Tag created and linked to user |
| `test_create_ingredient` | Ingredient created and linked to user |

### `test_admin.py`

| Test | Description |
|------|-------------|
| `test_users_listed` | Admin user list page returns HTTP 200 |
| `test_edit_user_page` | Admin user edit page returns HTTP 200 |
| `test_create_user_page` | Admin create user page returns HTTP 200 |

### `test_commands.py`

| Test | Description |
|------|-------------|
| `test_wait_for_db_ready` | Returns immediately when DB is available |
| `test_wait_for_db_delay_psycopg2_error` | Retries on psycopg2 error, eventually succeeds |
| `test_wait_for_db_delay_django_error` | Retries on Django OperationalError, eventually succeeds |
