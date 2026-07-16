# Week 3 Capstone — Full Production Stack

A containerised REST API demonstrating a multi-database architecture:
PostgreSQL (structured data), MongoDB (unstructured logs), Redis (caching),
and Nginx (reverse proxy).

## Architecture
- **PostgreSQL** — permanent storage for `tasks` (id, title, status, created_at)
- **MongoDB** — stores unstructured request logs (`request_logs` collection)
- **Redis** — caches `GET /tasks/<id>` responses for 60 seconds (cache-aside pattern)
- **Nginx** — reverse proxy; only entry point into the stack
- **Flask app** — REST API, built with a multi-stage Dockerfile for a minimal final image

## Endpoints

| Method | Path            | Description                              |
|--------|-----------------|-------------------------------------------|
| GET    | `/health`       | Basic liveness check                      |
| POST   | `/tasks`        | Create a task (Postgres write + Mongo log)|
| GET    | `/tasks/<id>`   | Get a task (Redis cache, falls back to Postgres) |
| GET    | `/logs`         | View all MongoDB request logs             |

## Prerequisites

- Docker and Docker Compose installed
- Ports 5433, 27018, 6380, and 8080 free on your host machine

## Setup & Deployment

1. Clone this repository:
```bash
   git clone <your-repo-url>
   cd week3-capstone
```

2. Build and start all services:
```bash
   docker compose up --build -d
```

3. Verify all services are healthy:
```bash
   ./healthcheck.sh
```

4. Test the API (through Nginx, port 8080):
```bash
   curl http://localhost:8080/health

   curl -X POST http://localhost:8080/tasks \
     -H "Content-Type: application/json" \
     -d '{"title": "Buy groceries"}'

   curl http://localhost:8080/tasks/1

   curl http://localhost:8080/logs
```

5. Stop the stack:
```bash
   docker compose down
```

   To also remove stored data (Postgres/Mongo volumes):
```bash
   docker compose down -v
```

## Known Limitations / Future Improvements

- Database connections are created once at app startup rather than pooled;
  a production version would use a connection pool (e.g. `psycopg2.pool`)
  for resilience against DB restarts and higher concurrency.
- No authentication on the API endpoints.
- Redis cache uses a fixed 60-second TTL rather than active invalidation on update.

## Tech Stack

- Python 3.12 / Flask
- PostgreSQL 16
- MongoDB 7
- Redis 7
- Nginx (alpine)
- Docker Compose
