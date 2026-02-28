# user — Authentication & Profile App

[![Python](https://img.shields.io/badge/Python-3.9-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![DRF](https://img.shields.io/badge/Django_REST_Framework-3.12-ff1709?style=flat-square&logo=django&logoColor=white)](https://www.django-rest-framework.org/)

The `user` app handles all user-facing authentication operations: account creation, token-based login, and profile management. It exposes three REST endpoints and contains no models — all data lives in `core.User`.

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
user/
├── serializers.py       # Input validation + user creation/update logic
├── views.py             # Three API views (create, token, profile)
├── urls.py              # Route definitions under /api/user/
└── tests/
    └── test_user_api.py # Full endpoint test suite (public + private)
```

---

## Data Flow

```
HTTP Request
     │
     ▼
URL Router  (/api/user/*)
     │
     ▼
View  (CreateUserView / CreateTokenView / ManageUserView)
     │
     ├──▶  Authentication check  (token required for ManageUserView)
     │
     ▼
Serializer  (UserSerializer / AuthTokenSerializer)
     │
     ├──▶  Validation error  ──▶  400 Bad Request
     │
     ▼
core.User model  (via Django ORM)
     │
     ▼
JSON Response
```

---

## Serializers

### `UserSerializer`

Handles user **registration** and **profile updates**.

| Field | Type | Constraints |
|-------|------|-------------|
| `email` | string | required, valid email format |
| `password` | string | write-only, min_length=5 |
| `name` | string | required |

**Custom methods:**

- **`create(validated_data)`** — calls `User.objects.create_user(**validated_data)`, ensuring the password is hashed via `make_password` before storage. Never stores plaintext passwords.
- **`update(instance, validated_data)`** — pops `password` from the update payload, hashes it via `set_password`, then saves. Other fields update normally.

---

### `AuthTokenSerializer`

Handles **login** by validating credentials and returning the authenticated user object.

| Field | Type | Description |
|-------|------|-------------|
| `email` | string | User's email address |
| `password` | string | User's password (write-only) |

**Custom `validate(attrs)`:**
1. Calls `authenticate(request, username=email, password=password)`
2. If authentication fails → raises `ValidationError('Unable to authenticate with provided credentials')`
3. If successful → attaches `user` to validated attrs for the view to consume

---

## Views

### `CreateUserView`

```
Class:    generics.CreateAPIView
Method:   POST
Auth:     None (public endpoint)
Purpose:  Register a new user account
```

Uses `UserSerializer`. On valid data, creates the user and returns `201 Created` with email and name. Returns `400 Bad Request` with field-level error messages on validation failure.

---

### `CreateTokenView`

```
Class:    ObtainAuthToken
Method:   POST
Auth:     None (public endpoint)
Purpose:  Authenticate and return an API token
```

Uses `AuthTokenSerializer`. On valid credentials, retrieves or creates a `Token` record and returns it. Returns `400 Bad Request` on invalid credentials.

---

### `ManageUserView`

```
Class:    generics.RetrieveUpdateAPIView
Methods:  GET, PUT, PATCH
Auth:     TokenAuthentication + IsAuthenticated (required)
Purpose:  View or update the authenticated user's profile
```

The view self-identifies the user via `request.user` — no user ID in the URL. `POST` is not allowed (returns `405 Method Not Allowed`).

---

## URL Routes

Mounted at `/api/user/` in the root `urls.py`.

| Pattern | View | Name |
|---------|------|------|
| `create/` | `CreateUserView` | `create` |
| `token/` | `CreateTokenView` | `token` |
| `me/` | `ManageUserView` | `me` |

---

## API Endpoints

### Register

```http
POST /api/user/create/
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "mypassword",
  "name": "Jane Doe"
}
```

**Success `201 Created`:**
```json
{
  "email": "user@example.com",
  "name": "Jane Doe"
}
```

**Error `400 Bad Request`** (email taken):
```json
{
  "email": ["user with this email address already exists."]
}
```

---

### Login (obtain token)

```http
POST /api/user/token/
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "mypassword"
}
```

**Success `200 OK`:**
```json
{
  "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
}
```

**Error `400 Bad Request`** (wrong credentials):
```json
{
  "non_field_errors": ["Unable to authenticate with provided credentials."]
}
```

---

### View profile

```http
GET /api/user/me/
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
```

**Success `200 OK`:**
```json
{
  "email": "user@example.com",
  "name": "Jane Doe"
}
```

---

### Update profile

```http
PATCH /api/user/me/
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
Content-Type: application/json

{
  "name": "Jane Smith",
  "password": "newpassword123"
}
```

**Success `200 OK`:**
```json
{
  "email": "user@example.com",
  "name": "Jane Smith"
}
```

---

## Tests

All tests are in `tests/test_user_api.py` and run with `python manage.py test user`.

### `PublicUserApiTests` (no authentication)

| Test | Description |
|------|-------------|
| `test_create_user_success` | Valid payload creates user, returns `201` |
| `test_user_with_email_exists_error` | Duplicate email returns `400` |
| `test_password_too_short_error` | Password under 5 chars returns `400` |
| `test_create_token_for_user` | Valid credentials return token |
| `test_create_token_bad_credentials` | Wrong password returns `400` |
| `test_create_token_blank_password` | Empty password returns `400` |
| `test_retrieve_user_unauthorized` | No token returns `401` on `/me/` |

### `PrivateUserApiTests` (authenticated)

| Test | Description |
|------|-------------|
| `test_retrieve_profile_success` | Authenticated GET `/me/` returns user data |
| `test_post_me_not_allowed` | POST to `/me/` returns `405` |
| `test_update_user_profile` | PATCH `/me/` updates name and password |
