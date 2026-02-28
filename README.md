<div align="center">

<img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=32&duration=3000&pause=1000&color=22C55E&center=true&vCenter=true&width=700&lines=Recipe+App+API;Django+REST+Framework+Backend;Production-Ready+Architecture;Dockerized+%7C+Tested+%7C+OpenAPI+Docs" alt="Typing SVG" />

<br/>

[![Python](https://img.shields.io/badge/Python-3.9-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-3.2-092E20?style=for-the-badge&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/Django_REST_Framework-3.12-ff1709?style=for-the-badge&logo=django&logoColor=white)](https://www.django-rest-framework.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13-316192?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-CI%2FCD-2088FF?style=for-the-badge&logo=github-actions&logoColor=white)](https://github.com/features/actions)
[![Swagger](https://img.shields.io/badge/Swagger-OpenAPI-85EA2D?style=for-the-badge&logo=swagger&logoColor=black)](https://swagger.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

<br/>

**A production-ready RESTful API backend for recipe management, built with Django REST Framework, containerized with Docker, and documented with OpenAPI/Swagger.**

[Architecture](#architecture) · [API Reference](#api-reference) · [Running the Project](#running-the-project) · [Engineering Highlights](#engineering-highlights)

</div>

---

## Table of Contents

- [Project Overview](#project-overview)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Features](#features)
- [Project Structure](#project-structure)
- [Database Schema](#database-schema)
- [API Reference](#api-reference)
- [Authentication](#authentication)
- [Running the Project](#running-the-project)
- [Running Tests](#running-tests)
- [CI/CD Pipeline](#cicd-pipeline)
- [Engineering Highlights](#engineering-highlights)

---

## Project Overview

**Recipe App API** is a fully-featured REST API backend that enables users to manage their personal recipe collections. Users register and authenticate via token-based auth, then can create, read, update, and delete recipes enriched with tags, ingredients, and image uploads.

This project demonstrates production-grade backend engineering practices:

- **Custom user model** with email-based authentication replacing Django's default username model
- **Token authentication** via DRF `TokenAuthentication`, scoping all data to the requesting user
- **Nested serializer relationships** for handling many-to-many associations (recipes ↔ tags ↔ ingredients)
- **Containerized full-stack environment** — API and database run entirely in Docker with a single command
- **Automated CI/CD** — every push runs the full test suite and linter through GitHub Actions
- **Auto-generated OpenAPI 3.0 documentation** via `drf-spectacular`, served through Swagger UI

---

## Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                  CLIENT (Browser / cURL / Frontend)              │
└─────────────────────────┬───────────────────────────────────────┘
                          │  HTTP Request (JSON + Auth Token)
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DOCKER NETWORK                              │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                  Django Application (Port 8000)            │   │
│  │                                                            │   │
│  │  ┌─────────────┐   ┌──────────────┐   ┌──────────────┐  │   │
│  │  │ URL Router  │──▶│   ViewSets   │──▶│ Serializers  │  │   │
│  │  │  (urls.py)  │   │  (views.py)  │   │              │  │   │
│  │  └─────────────┘   └──────┬───────┘   └──────┬───────┘  │   │
│  │                           │                   │           │   │
│  │                           ▼                   ▼           │   │
│  │                  ┌────────────────────────────────────┐  │   │
│  │                  │        Django ORM (Models)          │  │   │
│  │                  └─────────────────┬──────────────────┘  │   │
│  └────────────────────────────────────┼────────────────────-┘   │
│                                       │  SQL Queries             │
│  ┌────────────────────────────────────▼────────────────────┐    │
│  │              PostgreSQL 13  (Port 5432, internal)        │    │
│  └──────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

### API Request Flow

```
Incoming Request
      │
      ▼
URL Router (urls.py)
      │
      ▼
Authentication Middleware (TokenAuthentication)
      │
      ├── Invalid Token ──▶  401 Unauthorized
      │
      ▼
ViewSet / APIView
      │
      ▼
Permission Check (IsAuthenticated)
      │
      ├── Denied ──▶  403 Forbidden
      │
      ▼
Serializer (validate + deserialize input)
      │
      ├── Invalid Data ──▶  400 Bad Request
      │
      ▼
ORM Query (user-scoped queryset)
      │
      ▼
PostgreSQL Database
      │
      ▼
Serializer (serialize response data)
      │
      ▼
JSON Response  (200 / 201 / 204)
```

### Docker Architecture

```
┌──────────────────────────────────────────────────┐
│               docker-compose.yml                  │
│                                                    │
│  ┌──────────────────┐    ┌──────────────────┐    │
│  │   Service: app   │    │   Service: db    │    │
│  │                  │    │                  │    │
│  │  Python 3.9      │    │  PostgreSQL 13   │    │
│  │  Alpine Linux    │    │  Alpine          │    │
│  │  Port: 8000      │◀──▶│  Port: 5432      │    │
│  │  Volume: ./app   │    │  Volume: db-data │    │
│  │                  │    │                  │    │
│  │  Entrypoint:     │    │  Env vars:       │    │
│  │  wait_for_db     │    │  POSTGRES_DB     │    │
│  │  migrate         │    │  POSTGRES_USER   │    │
│  │  runserver       │    │  POSTGRES_PASSWORD│    │
│  └──────────────────┘    └──────────────────┘    │
└──────────────────────────────────────────────────┘
```

---

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Language | Python 3.9 | Core runtime |
| Web Framework | Django 3.2 | MVC structure, ORM, admin panel |
| API Framework | Django REST Framework 3.12 | Serialization, ViewSets, authentication |
| Database | PostgreSQL 13 | Relational data persistence |
| DB Adapter | psycopg2 | Python–PostgreSQL bridge |
| API Docs | drf-spectacular | OpenAPI 3.0 schema + Swagger UI |
| Image Processing | Pillow | Recipe image upload support |
| Containerization | Docker + Docker Compose | Reproducible dev/prod environments |
| CI/CD | GitHub Actions | Automated testing + linting on push |
| Linter | flake8 | PEP8 code style enforcement |

---

## Features

- **User Registration & Authentication** — email-based registration, token-based API auth
- **Recipe Management** — full CRUD: create, list, retrieve, partial/full update, delete
- **Tag System** — create and assign searchable tags to recipes
- **Ingredient System** — manage ingredients independently, attach to recipes
- **User-Scoped Data** — every query is automatically filtered to the authenticated user
- **Nested Serializers** — recipes return embedded tags and ingredients in a single response
- **Idempotent Create-or-Fetch** — posting an existing tag/ingredient name reuses the record
- **Image Uploads** — attach images to recipes via multipart form-data
- **Swagger UI** — interactive API explorer at `/api/docs/`
- **Django Admin** — full admin interface for superuser data management
- **Health-Aware Startup** — `wait_for_db` ensures the app never starts before PostgreSQL is ready
- **CI Tested** — 40+ unit and integration tests run automatically on every push

---

## Project Structure

```
recipe_app_api/
│
├── .github/
│   └── workflows/
│       └── checks.yml          # CI: run tests + lint on every push
│
├── app/                        # Django project root (mounted into Docker)
│   ├── manage.py               # Django management entry point
│   ├── .flake8                 # Linting configuration
│   │
│   ├── app/                    # Django project configuration package
│   │   ├── settings.py         # All project settings (DB, auth, installed apps)
│   │   ├── urls.py             # Root URL dispatcher
│   │   ├── wsgi.py             # WSGI entry point (production server)
│   │   └── asgi.py             # ASGI entry point (async support)
│   │
│   ├── core/                   # Shared foundation app
│   │   ├── models.py           # User, Recipe, Tag, Ingredient models
│   │   ├── admin.py            # Custom Django admin registrations
│   │   ├── migrations/         # Database migration history
│   │   ├── management/
│   │   │   └── commands/
│   │   │       └── wait_for_db.py  # DB readiness health check command
│   │   └── tests/
│   │       ├── test_models.py      # Model unit tests
│   │       ├── test_admin.py       # Admin interface tests
│   │       └── test_commands.py    # Management command tests
│   │
│   ├── user/                   # Authentication & user profile app
│   │   ├── serializers.py      # User + AuthToken serializers
│   │   ├── views.py            # Register, login, profile views
│   │   ├── urls.py             # /api/user/* URL routes
│   │   └── tests/
│   │       └── test_user_api.py    # Full user API test suite
│   │
│   └── recipe/                 # Core business logic app
│       ├── serializers.py      # Recipe, Tag, Ingredient serializers
│       ├── views.py            # Recipe, Tag, Ingredient ViewSets
│       ├── urls.py             # /api/recipe/* routes via DRF Router
│       └── tests/
│           ├── test_recipe_api.py      # Recipe endpoint tests
│           ├── test_tags_api.py        # Tag endpoint tests
│           └── test_ingredients_api.py # Ingredient endpoint tests
│
├── Dockerfile                  # Multi-stage Python/Alpine Docker image
├── docker-compose.yml          # App + DB service orchestration
├── requirements.txt            # Production dependencies
├── requirements.dev.txt        # Development dependencies (flake8)
└── LICENSE
```

---

## Database Schema

```
┌──────────────────────────────────────────────────────────────────┐
│                        DATABASE SCHEMA                            │
│                                                                    │
│  ┌─────────────────────┐       ┌──────────────────────────────┐  │
│  │        User         │       │           Recipe             │  │
│  │─────────────────────│       │──────────────────────────────│  │
│  │ id          (PK)    │──┐    │ id           (PK)            │  │
│  │ email       unique  │  │    │ user_id      (FK → User)     │  │
│  │ name                │  └───▶│ title                        │  │
│  │ is_active           │       │ description                  │  │
│  │ is_staff            │       │ time_minutes                 │  │
│  └─────────────────────┘       │ price                        │  │
│                                 │ link                         │  │
│                                 └──────────┬─────────────────-┘  │
│                                            │  M2M                 │
│                     ┌──────────────────────┤                      │
│                     │                      │                      │
│                     ▼                      ▼                      │
│  ┌──────────────────────────┐  ┌───────────────────────────┐     │
│  │          Tag             │  │        Ingredient          │     │
│  │──────────────────────────│  │───────────────────────────│     │
│  │ id       (PK)            │  │ id       (PK)              │     │
│  │ name                     │  │ name                       │     │
│  │ user_id  (FK → User)     │  │ user_id  (FK → User)       │     │
│  └──────────────────────────┘  └───────────────────────────┘     │
└──────────────────────────────────────────────────────────────────┘

Relationships:
  User     1 : N   Recipe       (a user owns many recipes)
  User     1 : N   Tag          (tags are user-scoped)
  User     1 : N   Ingredient   (ingredients are user-scoped)
  Recipe   M : N   Tag          (via recipe_tags join table)
  Recipe   M : N   Ingredient   (via recipe_ingredients join table)
```

---

## API Reference

### Base URL

```
http://localhost:8000/api
```

### Interactive Documentation

Visit **`http://localhost:8000/api/docs/`** for the full Swagger UI with live request testing.

---

### Authentication Endpoints

#### Register a new user

```http
POST /api/user/create/
Content-Type: application/json

{
  "email": "chef@example.com",
  "password": "securepass123",
  "name": "Gordon Ramsay"
}
```

**Response `201 Created`:**
```json
{
  "email": "chef@example.com",
  "name": "Gordon Ramsay"
}
```

---

#### Obtain auth token

```http
POST /api/user/token/
Content-Type: application/json

{
  "email": "chef@example.com",
  "password": "securepass123"
}
```

**Response `200 OK`:**
```json
{
  "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
}
```

> All subsequent requests must include: `Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b`

---

#### Get or update profile

```http
GET  /api/user/me/
PATCH /api/user/me/
Authorization: Token <your-token>
Content-Type: application/json

{
  "name": "Updated Name"
}
```

---

### Recipe Endpoints

#### List all recipes

```http
GET /api/recipe/recipes/
Authorization: Token <your-token>
```

**Response `200 OK`:**
```json
[
  {
    "id": 1,
    "title": "Beef Wellington",
    "time_minutes": 120,
    "price": "85.00",
    "link": "https://example.com/beef-wellington",
    "tags": [{ "id": 1, "name": "Dinner" }],
    "ingredients": [
      { "id": 1, "name": "Beef Tenderloin" },
      { "id": 2, "name": "Puff Pastry" }
    ]
  }
]
```

---

#### Create a recipe

```http
POST /api/recipe/recipes/
Authorization: Token <your-token>
Content-Type: application/json

{
  "title": "Spaghetti Carbonara",
  "time_minutes": 25,
  "price": "12.50",
  "description": "Classic Roman pasta.",
  "tags": [{ "name": "Italian" }, { "name": "Pasta" }],
  "ingredients": [
    { "name": "Spaghetti" },
    { "name": "Guanciale" },
    { "name": "Pecorino Romano" }
  ]
}
```

**Response `201 Created`:**
```json
{
  "id": 2,
  "title": "Spaghetti Carbonara",
  "time_minutes": 25,
  "price": "12.50",
  "description": "Classic Roman pasta.",
  "link": "",
  "tags": [
    { "id": 2, "name": "Italian" },
    { "id": 3, "name": "Pasta" }
  ],
  "ingredients": [
    { "id": 3, "name": "Spaghetti" },
    { "id": 4, "name": "Guanciale" },
    { "id": 5, "name": "Pecorino Romano" }
  ]
}
```

---

#### Partial update

```http
PATCH /api/recipe/recipes/2/
Authorization: Token <your-token>
Content-Type: application/json

{
  "time_minutes": 30
}
```

---

#### Full update

```http
PUT /api/recipe/recipes/2/
Authorization: Token <your-token>
Content-Type: application/json

{
  "title": "Spaghetti Carbonara",
  "time_minutes": 30,
  "price": "12.50"
}
```

---

#### Delete a recipe

```http
DELETE /api/recipe/recipes/2/
Authorization: Token <your-token>
```

**Response `204 No Content`**

---

### Tag & Ingredient Endpoints

```http
GET    /api/recipe/tags/               # List tags for authenticated user
PATCH  /api/recipe/tags/{id}/          # Update a tag
DELETE /api/recipe/tags/{id}/          # Delete a tag

GET    /api/recipe/ingredients/        # List ingredients for authenticated user
PATCH  /api/recipe/ingredients/{id}/   # Update an ingredient
DELETE /api/recipe/ingredients/{id}/   # Delete an ingredient
```

---

### Admin & Docs

```http
GET /admin/       # Django admin interface (superuser required)
GET /api/docs/    # Swagger UI — interactive API explorer
GET /api/schema/  # Raw OpenAPI 3.0 JSON schema download
```

---

## Authentication

This API uses **Token Authentication** (`rest_framework.authentication.TokenAuthentication`).

```
1. Register:   POST /api/user/create/   →  account created
2. Login:      POST /api/user/token/    →  { "token": "abc123..." }
3. Authorize:  Set header on all requests:
               Authorization: Token abc123...
```

**Security properties:**
- Passwords stored as bcrypt hashes via Django's `make_password` — never plaintext
- Tokens are user-scoped and persist until explicitly invalidated
- All querysets filter by `request.user` — cross-user data access is impossible
- Unauthenticated requests to protected endpoints return `401 Unauthorized`

---

## Running the Project

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (includes Docker Compose)

### 1. Clone the repository

```bash
git clone https://github.com/sadykovIsmail/recipe_app_api.git
cd recipe_app_api
```

### 2. Build the Docker image

```bash
docker-compose build
```

### 3. Start all services

```bash
docker-compose up
```

The startup sequence is automatic:
1. PostgreSQL starts
2. `wait_for_db` polls until DB accepts connections
3. `migrate` applies all schema migrations
4. Development server starts on **`http://localhost:8000`**

### 4. Create a superuser (optional)

```bash
docker-compose run --rm app sh -c "python manage.py createsuperuser"
```

Then visit `http://localhost:8000/admin/`.

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DB_HOST` | `db` | PostgreSQL service hostname |
| `DB_NAME` | `devdb` | Database name |
| `DB_USER` | `devuser` | Database user |
| `DB_PASS` | `changeme` | Database password |

---

## Running Tests

```bash
# Run full test suite
docker-compose run --rm app sh -c "python manage.py test"

# Run linter
docker-compose run --rm app sh -c "flake8"

# Run tests for a specific app
docker-compose run --rm app sh -c "python manage.py test core"
docker-compose run --rm app sh -c "python manage.py test user"
docker-compose run --rm app sh -c "python manage.py test recipe"
```

**Test coverage includes:**
- Model creation and validation (User, Recipe, Tag, Ingredient)
- Custom user manager (email normalization, superuser creation)
- Management commands (`wait_for_db` with simulated DB unavailability)
- Django admin views (list, edit, create user pages)
- All public and private API endpoints
- Token authentication flows
- Permission enforcement (unauthenticated access, cross-user data isolation)
- Nested serializer operations (create/update with embedded tags and ingredients)

---

## CI/CD Pipeline

GitHub Actions runs automatically on every push:

```
Trigger: push (any branch)

Jobs:
  1. Test
     └── docker-compose run app python manage.py test

  2. Lint
     └── docker-compose run app flake8
```

The pipeline ensures:
- No broken tests reach the main branch
- PEP8 code style is enforced via flake8
- The full Docker stack is tested end-to-end (not just local Python)

---

## Engineering Highlights

### REST API Design
Follows REST conventions throughout: resource-based URLs, correct HTTP verbs (`GET`, `POST`, `PUT`, `PATCH`, `DELETE`), and appropriate status codes (`200`, `201`, `204`, `400`, `401`, `403`, `404`). Uses DRF `ModelViewSet` with `DefaultRouter` for minimal-boilerplate, standards-compliant endpoint registration.

### Custom Authentication Model
Replaced Django's default `username`-based `User` model with a custom email-based implementation (`AUTH_USER_MODEL = 'core.User'`). Built a custom `UserManager` with dedicated `create_user` and `create_superuser` factory methods, ensuring clean password hashing at the model layer.

### Data Modeling & User Isolation
Designed a normalized relational schema with `ForeignKey` and `ManyToManyField` relationships. All querysets are filtered at the view layer by `request.user` — a user cannot access another user's resources, even by guessing resource IDs.

### Nested Serializer Patterns
Implemented writable nested serializers for `Recipe` ↔ `Tag` / `Ingredient` many-to-many relationships. The `_get_or_create_tags` and `_get_or_create_ingredients` patterns demonstrate idempotent resource creation — posting the same name twice reuses the existing record.

### Production-Grade Docker Setup
Full containerization: PostgreSQL and Django run in isolated containers orchestrated by Docker Compose. The custom `wait_for_db` management command is a robust startup probe — it retries on both `psycopg2.OperationalError` and Django's `OperationalError` to handle race conditions reliably.

### Test-Driven Development
All features were built test-first. The suite covers models, serializers, views, admin, and management commands using Django's `TestCase`, DRF's `APIClient`, and `unittest.mock.patch` for precise external dependency isolation.

### Auto-Generated API Documentation
Schema and Swagger UI are powered by `drf-spectacular` and derived directly from serializers and views — the documentation is always in sync with the implementation, with zero manual maintenance.

---

<div align="center">

Built with Python · Django REST Framework · PostgreSQL · Docker

</div>
