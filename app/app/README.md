# app — Django Project Configuration

[![Django](https://img.shields.io/badge/Django-3.2-092E20?style=flat-square&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/Django_REST_Framework-3.12-ff1709?style=flat-square&logo=django&logoColor=white)](https://www.django-rest-framework.org/)
[![Swagger](https://img.shields.io/badge/Swagger-OpenAPI_3.0-85EA2D?style=flat-square&logo=swagger&logoColor=black)](https://swagger.io/)

The `app/` package is the Django project configuration directory. It contains no models, serializers, or business logic — it is the wiring layer that ties together the installed apps, database connection, authentication settings, and root URL routing.

---

## Table of Contents

- [Overview](#overview)
- [Settings](#settings)
- [URL Routing](#url-routing)
- [WSGI / ASGI](#wsgi--asgi)

---

## Overview

```
app/
├── settings.py    # All project-wide settings
├── urls.py        # Root URL dispatcher
├── wsgi.py        # WSGI entry point (production servers)
├── asgi.py        # ASGI entry point (async support)
├── calc.py        # Utility module (add, subtract)
└── tests.py       # Unit tests for calc.py
```

---

## Settings

`settings.py` controls every aspect of the Django project.

### Key Settings

#### Database

PostgreSQL connection is configured entirely via environment variables, making it portable across Docker, CI, and production environments:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'HOST':   os.environ.get('DB_HOST'),
        'NAME':   os.environ.get('DB_NAME'),
        'USER':   os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASS'),
    }
}
```

| Variable | Docker Default | Description |
|----------|---------------|-------------|
| `DB_HOST` | `db` | Service name in docker-compose |
| `DB_NAME` | `devdb` | Database name |
| `DB_USER` | `devuser` | Database user |
| `DB_PASS` | `changeme` | Database password |

---

#### Custom User Model

```python
AUTH_USER_MODEL = 'core.User'
```

Overrides Django's default `auth.User` with the project's email-based custom user model. This setting must be set before the first migration is created and should never be changed afterwards.

---

#### Installed Apps

```python
INSTALLED_APPS = [
    # Django builtins
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party
    'rest_framework',
    'rest_framework.authtoken',
    'drf_spectacular',

    # Project apps
    'core',
    'user',
    'recipe',
]
```

---

#### REST Framework

```python
REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}
```

Wires `drf-spectacular` as the schema generator for all ViewSets, enabling auto-generated OpenAPI 3.0 documentation without any manual annotations.

---

#### Static Files

```python
STATIC_URL = '/static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = '/vol/web/media'
STATIC_ROOT = '/vol/web/static'
```

Media root is set to a Docker volume path for persistent image storage.

---

## URL Routing

`urls.py` is the single root URL dispatcher. All application routes are delegated via `include()`:

```
/admin/          ──▶  Django Admin
/api/schema/     ──▶  SpectacularAPIView  (raw OpenAPI JSON)
/api/docs/       ──▶  SpectacularSwaggerView  (Swagger UI)
/api/user/       ──▶  user.urls
/api/recipe/     ──▶  recipe.urls
```

### Route Table

| URL | View | Description |
|-----|------|-------------|
| `/admin/` | `admin.site.urls` | Django admin interface |
| `/api/schema/` | `SpectacularAPIView` | OpenAPI 3.0 schema (JSON/YAML) |
| `/api/docs/` | `SpectacularSwaggerView` | Interactive Swagger UI |
| `/api/user/create/` | `CreateUserView` | Register a new user |
| `/api/user/token/` | `CreateTokenView` | Obtain auth token |
| `/api/user/me/` | `ManageUserView` | View/update profile |
| `/api/recipe/recipes/` | `RecipeViewSet` | Recipe CRUD |
| `/api/recipe/tags/` | `TagViewSet` | Tag management |
| `/api/recipe/ingredients/` | `IngredientViewSet` | Ingredient management |

---

## WSGI / ASGI

### `wsgi.py`

Standard Django WSGI application, used by production servers like Gunicorn or uWSGI:

```python
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
application = get_wsgi_application()
```

### `asgi.py`

Standard Django ASGI application, enabling future async support with servers like Uvicorn or Daphne:

```python
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
application = get_asgi_application()
```
