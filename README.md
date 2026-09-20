# Bazaarly Backend

Multi-vendor marketplace backend built with FastAPI, SQLModel (async), and PostgreSQL.

## Quick Start

```bash
# 1. Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # on Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -e ".[dev]"

# 3. Copy env file
cp .env.example .env
# Edit .env with your database URL and secrets

# 4. Start Postgres (Docker)
docker compose up -d postgres

# 5. Run migrations
alembic upgrade head

# 6. Seed the database
python -m app.db.seed

# 7. Start the server
uvicorn app.main:app --reload
```

## API Docs

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

## Test Accounts (after seeding)

| Email | Password | Role |
|---|---|---|
| admin@bazaarly.com | password123 | admin |
| seller@bazaarly.com | password123 | seller |
| seller2@bazaarly.com | password123 | seller |
| customer@bazaarly.com | password123 | customer |
| customer2@bazaarly.com | password123 | customer |

## API Endpoints

### Auth (public)
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh`
- `POST /api/v1/auth/logout`
- `GET  /api/v1/auth/me`

### Users
- `GET    /api/v1/users/me`
- `PATCH  /api/v1/users/me`

### Sellers
- `GET    /api/v1/sellers`
- `GET    /api/v1/sellers/me`
- `PATCH  /api/v1/sellers/me`
- `GET    /api/v1/sellers/{seller_id}`
- `GET    /api/v1/sellers/{seller_id}/products`

### Products
- `GET    /api/v1/products` (admin)
- `GET    /api/v1/products/mine` (seller)
- `GET    /api/v1/products/{id}`
- `POST   /api/v1/products` (seller)
- `PATCH  /api/v1/products/{id}` (seller owner)
- `DELETE /api/v1/products/{id}` (seller owner)
- `POST   /api/v1/products/{id}/approve` (admin)
- `POST   /api/v1/products/{id}/reject` (admin)

### Orders
- `POST   /api/v1/orders/checkout` (customer)
- `POST   /api/v1/orders/confirm` (customer)
- `GET    /api/v1/orders/mine` (customer)
- `GET    /api/v1/orders/seller/mine` (seller)
- `GET    /api/v1/orders/{id}`
- `POST   /api/v1/orders/{id}/accept` (seller owner)
- `POST   /api/v1/orders/{id}/ship` (seller owner)
- `POST   /api/v1/orders/{id}/deliver` (seller owner)
- `POST   /api/v1/orders/{id}/cancel` (customer or seller owner)

### Admin
- `GET /api/v1/admin/stats`
- `GET /api/v1/admin/sellers`
- `GET /api/v1/admin/orders`

### Payments
- `POST /api/v1/payments/create-intent` (customer)
- `POST /api/v1/payments/webhook` (public)

### Uploads
- `POST /api/v1/uploads/presign` (seller)
- `POST /api/v1/uploads` (seller)

## Running Tests

```bash
pytest tests/ -v
```

## Docker

```bash
docker compose up --build
```

## Architecture

- **Routers** in `app/api/v1/` — HTTP concerns only, call services
- **Services** in `app/services/` — business logic and DB access
- **Models** in `app/models/` — SQLModel ORM tables
- **Schemas** in `app/schemas/` — Pydantic v2 request/response shapes
- **Core** in `app/core/` — config, security, deps, errors
- **DB** in `app/db/` — engine, session factory, seed script

## What's Stubbed

| Area | Status |
|---|---|
| Models + Schemas | Fully defined |
| All endpoint routes | Implemented, wire to DB |
| Auth (JWT) | Implemented (bcrypt + jose) |
| Order state machine | Enforced in order_service |
| Seed script | Fully working, deterministic UUIDs |
| Stripe payments | Stub (needs live keys) |
| S3 uploads | Stub (needs live bucket) |
| Background workers | Stub (Celery/RQ to add) |
| Rate limiting | Stub (slowapi imported, needs middleware) |

## Next Steps

1. Wire rate limiting middleware
2. Implement Stripe webhook handler
3. Add S3 presigned URL logic
4. Add email/notification workers
5. Add input validation / Pydantic validators
6. Write full test suite
7. Add CI/CD pipeline
