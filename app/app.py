from flask import Flask, jsonify, request, Response
import psycopg2
import pymongo
import redis
import os
import json
import time
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

app = Flask(__name__)

# PostgreSQL connection
pg_conn = psycopg2.connect(
    host=os.environ.get("PG_HOST", "postgres"),
    port=os.environ.get("PG_PORT", "5432"),
    dbname=os.environ.get("PG_DB", "capstone_db"),
    user=os.environ.get("PG_USER", "admin"),
    password=os.environ.get("PG_PASSWORD", "admin123")
)
pg_conn.autocommit = True

with pg_conn.cursor() as cur:
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT NOW()
        )
    """)

# MongoDB connection
mongo_client = pymongo.MongoClient(
    os.environ.get("MONGO_URI", "mongodb://mongo:27017/")
)
mongo_db = mongo_client["capstone_logs"]
logs_collection = mongo_db["request_logs"]

# Redis connection
redis_client = redis.Redis(
    host=os.environ.get("REDIS_HOST", "redis"),
    port=int(os.environ.get("REDIS_PORT", "6379")),
    decode_responses=True
)

# ---------- Prometheus metrics ----------
REQUEST_COUNT = Counter(
    "app_requests_total", "Total number of requests", ["method", "endpoint", "status"]
)
REQUEST_LATENCY = Histogram(
    "app_request_latency_seconds", "Request latency in seconds", ["endpoint"]
)

@app.before_request
def start_timer():
    request.start_time = time.time()

@app.after_request
def record_metrics(response):
    latency = time.time() - request.start_time
    REQUEST_LATENCY.labels(endpoint=request.path).observe(latency)
    REQUEST_COUNT.labels(
        method=request.method, endpoint=request.path, status=response.status_code
    ).inc()
    return response

@app.route("/metrics")
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)
# -----------------------------------------

@app.route("/health")
def health():
    return jsonify({"status": "ok"})

@app.route("/tasks", methods=["POST"])
def create_task():
    data = request.get_json()
    title = data.get("title")

    with pg_conn.cursor() as cur:
        cur.execute(
            "INSERT INTO tasks (title) VALUES (%s) RETURNING id, title, status, created_at",
            (title,)
        )
        row = cur.fetchone()

    task = {
        "id": row[0],
        "title": row[1],
        "status": row[2],
        "created_at": str(row[3])
    }

    logs_collection.insert_one({
        "action": "create_task",
        "task_id": task["id"],
        "title": task["title"]
    })

    return jsonify(task), 201

@app.route("/tasks/<int:task_id>", methods=["GET"])
def get_task(task_id):
    cache_key = f"task:{task_id}"
    cached = redis_client.get(cache_key)
    if cached:
        result = json.loads(cached)
        result["source"] = "cache"
        return jsonify(result)

    with pg_conn.cursor() as cur:
        cur.execute(
            "SELECT id, title, status, created_at FROM tasks WHERE id = %s",
            (task_id,)
        )
        row = cur.fetchone()

    if row is None:
        return jsonify({"error": "task not found"}), 404

    task = {
        "id": row[0],
        "title": row[1],
        "status": row[2],
        "created_at": str(row[3]),
        "source": "database"
    }

    redis_client.setex(cache_key, 60, json.dumps(task))
    return jsonify(task)

@app.route("/logs", methods=["GET"])
def get_logs():
    logs = list(logs_collection.find({}, {"_id": 0}))
    return jsonify(logs)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
