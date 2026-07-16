#!/bin/bash

echo "Checking all services..."
echo ""

# Check PostgreSQL
if docker exec capstone_postgres pg_isready -U admin > /dev/null 2>&1; then
    echo "PostgreSQL: UP"
else
    echo "PostgreSQL: DOWN"
fi

# Check MongoDB
if docker exec capstone_mongo mongosh --eval "db.adminCommand('ping')" > /dev/null 2>&1; then
    echo "MongoDB: UP"
else
    echo "MongoDB: DOWN"
fi

# Check Redis
if docker exec capstone_redis redis-cli ping > /dev/null 2>&1; then
    echo "Redis: UP"
else
    echo "Redis: DOWN"
fi

# Check Flask app (via Nginx)
if curl -s -f http://localhost:8080/health > /dev/null 2>&1; then
    echo "App (via Nginx): UP"
else
    echo "App (via Nginx): DOWN"
fi

echo ""
echo "Health check complete."
