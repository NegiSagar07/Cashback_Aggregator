# Cashback Aggregator

A powerful, production-ready platform for aggregating, managing, and distributing cashback coupons and offers across multiple sources and channels.  
Built for reliability, scalability, and developer productivity—leveraging asynchronous Python technologies, a robust API layer, background task processing, and a modern containerized workflow.

---

## Table of Contents

- [Project Overview](#project-overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Directory Structure](#directory-structure)
- [Docker Setup (Recommended)](#docker-setup-recommended)
- [Environment Variables](#environment-variables)
- [Database Migrations](#database-migrations)
- [Running Tests](#running-tests)
- [Key Endpoints](#key-endpoints)
- [Background Tasks with Celery](#background-tasks-with-celery)
- [Authentication](#authentication)
- [Contributing](#contributing)
- [License](#license)

---

## Project Overview

Cashback Aggregator enables collecting, validating, and managing cashback and coupon offers from various sources, empowering campaign management and user incentives.  
Its robust backend provides RESTful APIs for web/mobile integration, user authentication with role management, background job support, and is cloud-native via Docker Compose.

**Use Cases:**
- Aggregate cashback from partners or merchants
- Distribute coupon codes per business rules
- Provide a secure backend for mobile/web
- Run scheduled bulk operations (validation, notifications, cleanup)
- Easily scale in any Docker-enabled environment

---

## Features

- User authentication & registration (JWT-based)
- CRUD for coupons and cashback offers
- Async, highly performant API endpoints (FastAPI)
- Role-based access control (RBAC)
- Background jobs with Celery & Redis
- API schema/documentation (Swagger/OpenAPI)
- Comprehensive health checks
- Modular, extensible Python codebase
- Ready-to-use local deployment (one-command with Docker Compose)

---

## Tech Stack

- **Language:** Python 3.10+
- **API:** FastAPI (ASGI)
- **ORM:** SQLAlchemy (async)
- **Database:** PostgreSQL
- **Task Queue:** Celery
- **Broker / Cache:** Redis
- **Migrations:** Alembic
- **Server:** Uvicorn
- **Authentication:** JWT (python-jose, passlib)
- **Testing:** pytest, pytest-asyncio
- **Templating:** Jinja2
- **Containerization:** Docker & Docker Compose (v2+)

---

## Architecture

- **FastAPI** handles all API endpoints (user, coupon, admin, etc.).
- **Async SQLAlchemy** for scalable, non-blocking DB transactions.
- **PostgreSQL** as the main data store.
- **Redis** broker for background jobs (Celery).
- **Alembic** manages schema migrations.
- **Docker Compose** orchestrates all services, enabling a ready-to-use stack.

```
┌─────────────┐       ┌─────────────┐      ┌────────────┐
│   Clients   │ ───▶  │  FastAPI    │ ───▶ │ PostgreSQL │
└─────────────┘       └─────────────┘      └────────────┘
       ▲   │  (REST/OpenAPI)  │
       │   └──────────────────┘
       │                       │
       └─────────────┬─────────┘
                     ▼
              ┌────────────┐
              │   Redis    │
              └─────┬──────┘
                    │
              ┌─────▼──────┐
              │   Celery   │
              └────────────┘
```

---

## Directory Structure

```
.
├── alembic/                  # Database migration scripts
├── app/
│   ├── api/                  # API routers (auth, coupon, etc.)
│   ├── core/                 # Config, security, utilities
│   ├── crud/                 # Data access
│   ├── services/             # Business logic, background tasks
│   ├── templates/            # Jinja2 templates (optional)
│   ├── auth.py, main.py, ... # App modules
├── docker/                   # Docker helpers/scripts
├── tests/                    # Unit & integration tests
├── requirements.txt          # Python dependencies
├── docker-compose.yml        # Describes the stack (api, db, redis, celery, etc.)
├── Dockerfile                # API container definition
├── alembic.ini               # Migration config
└── ...                       # Additional scripts & configs
```

---

## Docker Setup (Recommended)

> **Requires [Docker](https://www.docker.com/) and [Docker Compose v2+](https://docs.docker.com/compose/).**

1. **Clone the repository:**
   ```sh
   git clone https://github.com/NegiSagar07/Cashback_Aggregator.git
   cd Cashback_Aggregator
   ```

2. **Configure environment:**
   - Copy `.env.example` to `.env` and set secrets:
     ```sh
     cp .env.example .env
     # Edit .env as needed
     ```

3. **Build and launch everything:**
   ```sh
   docker compose up --build
   ```
   > This starts: API (Uvicorn/FastAPI), PostgreSQL, Redis, and Celery workers.

4. **Apply database migrations:**
   ```sh
   docker compose exec api alembic upgrade head
   ```

5. **(Optional) Seed the database:**
   ```sh
   docker compose exec api python seed_coupons.py
   ```

6. **Access the API:**
   - Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
   - Redoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## Environment Variables

- Configure your secrets in the `.env` file:
    - `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, `DB_HOST`
    - `REDIS_URL`
    - `SECRET_KEY`, `JWT_ALGORITHM`
    - (Add any project-specific variables)
- See `.env.example` for guidance.

---

## Database Migrations

- Alembic controls schema changes:
  ```sh
  docker compose exec api alembic revision --autogenerate -m "message"
  docker compose exec api alembic upgrade head
  ```
- Use these commands inside the running stack.

---

## Running Tests

- Run tests in the API container:
  ```sh
  docker compose exec api pytest
  ```

---

## Key Endpoints

- `/auth/register` — User signup
- `/auth/login` — User login / JWT token issue
- `/coupons/` — List, create, update, delete coupons (protected)
- `/health/db` — Database health check
- Full API documentation at `/docs`

---

## Background Tasks with Celery

- Celery worker runs as its own service in Compose.
- To start/debug manually:
  ```sh
  docker compose exec worker celery -A app.services.worker worker --loglevel=info
  ```
- Used for sending notifications, periodic coupon updates, etc.

---

## Authentication

- All secure endpoints require JWT authentication.
- Obtain your token from `/auth/login` then use as:
  ```
  Authorization: Bearer <your-token>
  ```
- Passwords are securely hashed; RBAC is enforced at API layer.

---

## Contributing

- Fork, then create a feature branch from `main`
- Write meaningful commit messages and clear PR descriptions
- Add or update tests for your code
- Ensure all tests pass

---

## License

See [LICENSE](LICENSE) (MIT).

---

**Found a bug or have an idea? Open an issue or join the discussion!**
