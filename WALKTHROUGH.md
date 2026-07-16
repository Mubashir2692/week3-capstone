# Week 3 Capstone — Walkthrough

This walkthrough demonstrates the full stack running end-to-end: Nginx to
Flask API to PostgreSQL / MongoDB / Redis, plus the bonus Prometheus and
CI/CD features.

## 1. Start the stack

Command: docker compose up --build -d

Result: All 5 containers (Postgres, MongoDB, Redis, the Flask app, and
Nginx) built and started successfully. Each showed "Healthy" for Postgres,
MongoDB, and Redis before the app container was created, confirming that
depends_on: condition: service_healthy correctly waited for real readiness,
not just container startup.

## 2. Verify all services are healthy

Command: ./healthcheck.sh

Output:
  PostgreSQL: UP
  MongoDB: UP
  Redis: UP
  App (via Nginx): UP
  Health check complete.

## 3. Create a task (PostgreSQL write + MongoDB log)

Command:
  curl -X POST http://localhost:8080/tasks -H "Content-Type: application/json" -d '{"title": "Buy groceries"}'

Response:
  {"created_at":"2026-07-16 06:25:57.810937","id":1,"status":"pending","title":"Buy groceries"}

The task was saved permanently in PostgreSQL (note the auto-generated id
and created_at, returned via SQL's RETURNING clause), and a corresponding
log entry was written to MongoDB in the same request.

## 4. Read the task - first request (cache miss)

Command: curl http://localhost:8080/tasks/1

Response:
  {"created_at":"2026-07-16 06:25:57.810937","id":1,"source":"database","status":"pending","title":"Buy groceries"}

"source":"database" confirms Redis had nothing cached yet, so PostgreSQL
answered the request, and the result was then cached with a 60-second TTL.

## 5. Read the same task again - cache hit

Command: curl http://localhost:8080/tasks/1

Response:
  {"created_at":"2026-07-16 06:25:57.810937","id":1,"source":"cache","status":"pending","title":"Buy groceries"}

"source":"cache" confirms Redis served this second request directly,
without touching PostgreSQL at all - the cache-aside pattern working
exactly as designed.

## 6. View MongoDB logs

Command: curl http://localhost:8080/logs

Response:
  [{"action":"create_task","task_id":1,"title":"Buy groceries"}]

## 7. Prometheus metrics

Command: curl http://localhost:8080/metrics

Sample output:
  app_requests_total{endpoint="/tasks/1",method="GET",status="200"} 2.0
  app_request_latency_seconds_sum{endpoint="/tasks/1"} 0.006679534912109375

Real request counts and latency histograms, broken down by method,
endpoint, and status, are exposed for scraping by a Prometheus server.

## 8. CI/CD pipeline

Every push to main triggers a GitHub Actions workflow that builds the
Docker image and pushes it to Docker Hub automatically.

- Workflow file: .github/workflows/ci.yml
- Image: mubashir2692/week3-capstone-app on Docker Hub
- Verified passing (green checkmark) in the repo's Actions tab.

## Summary

| Requirement                          | Status |
|---------------------------------------|--------|
| REST API, 2+ DB-backed endpoints       | Done (3 endpoints) |
| PostgreSQL with persistent volume      | Done |
| MongoDB secondary store                | Done |
| Redis caching                          | Done (proven live above) |
| Nginx reverse proxy                    | Done |
| Multi-stage Dockerfile                 | Done |
| docker-compose.yml                     | Done |
| Health check shell script              | Done |
| README                                 | Done |
| Bonus: GitHub Actions CI               | Done |
| Bonus: Prometheus metrics              | Done |
