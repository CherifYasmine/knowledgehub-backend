# KnowledgeHub Backend

This repository contains the backend API for KnowledgeHub — a content/wiki-style platform built with Django and Django REST Framework.

The API provides resources for Articles, Sections, Revisions, and Comments. Authentication uses JWT (SimpleJWT). API docs are available via drf-spectacular.

## Quick overview

- Framework: Django 5.2
- REST: Django REST Framework
- Auth: djangorestframework-simplejwt (access + refresh tokens)
- API docs: drf-spectacular (OpenAPI + Swagger UI)
- Code quality: pre-commit hooks (black, flake8)

## Repo structure (important files)

- `wiki/` - models, serializers, views for Article, Section, Revision
- `comments/` - Comment model (GenericForeignKey), votes
- `knowledgehub/settings/` - Django settings (SIMPLE_JWT, drf-spectacular config)
- `README.md` - this file

## Setup (local development)

Prerequisites

- Python 3.11+ (virtualenv recommended)
- PostgreSQL or other supported DB (project uses Django ORM)

Steps

1. Create & activate a virtualenv
    ```
    python -m venv .venv
    source .venv/bin/activate
    ```

2. Install dependencies
    ```
    pip install -r requirements.txt
    ```

3. Configure environment variables / settings

- Copy any sample settings/env files your project provides (e.g. `.env.example`) and set DB credentials, SECRET_KEY, and DEBUG as needed.

4. Apply migrations
    ```
    python manage.py migrate
    ```
5. Create a superuser
    ```
    python manage.py createsuperuser
    ```
6. Run the dev server
    ```
    python manage.py runserver
    ```

## Testing with Docker Compose

If you prefer to run the test suite inside containers, a `docker-compose.yml` is provided which brings up a PostgreSQL and Redis service and runs Django tests inside a `web` service.

1. Build and run the test compose (from the repo root):

```bash
docker compose -f docker-compose.yml up --build --abort-on-container-exit
```

2. When the tests finish the `web` container will exit. To view logs for the test run use:

```bash
docker compose -f docker-compose.yml logs web
```

3. Clean up resources (volumes, containers):

```bash
docker compose -f docker-compose.yml down -v
```

## API documentation

The project uses drf-spectacular to auto-generate OpenAPI schema and serve Swagger UI.

- Schema: `/api/schema/`
- Swagger UI: `/api/docs/`

Example auth flow (curl)

1. Obtain tokens (replace with your username/password)
    ```bash
    curl -X POST -H "Content-Type: application/json" -d '{"username":"<user>","password":"<pass>"}' http://127.0.0.1:8000/api/token/
    ```
Response will include `access` and `refresh` tokens.

2. Use access token for requests
    ```bash
    curl -H "Authorization: Bearer <ACCESS_TOKEN>" http://127.0.0.1:8000/api/articles/
    ```

## Code quality / pre-commit

This project uses pre-commit hooks to enforce formatting and linting. To run them locally:

    pre-commit run --all-files
