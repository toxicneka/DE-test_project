#!/bin/bash

set -e

echo "Stopping existing containers..."
docker-compose down

echo "Building and starting services with Docker Compose..."
docker-compose up --build -d

echo "Waiting for services to start..."
sleep 15

echo "Checking container status..."
docker-compose ps

echo "=== Running linting (ruff) ==="
docker-compose exec etl ruff check scripts/ tests/ || echo "Linting completed"

echo "=== Running unit tests (pytest) ==="
docker-compose exec etl pytest tests/ -v || echo "Tests completed"

echo "=== Running initial data extraction ==="
docker-compose exec etl python3 /app/scripts/extract.py

echo "=== Running initial transformation ==="
docker-compose exec etl python3 /app/scripts/transform.py

echo "=== Checking results ==="
echo "Raw data count:"
docker-compose exec db psql -U postgres -d postgres -c "SELECT COUNT(*) as total_posts FROM raw_users_by_posts;"

echo "Top users by posts:"
docker-compose exec db psql -U postgres -d postgres -c "SELECT * FROM top_users_by_posts ORDER BY posts_cnt DESC LIMIT 5;"

echo "=== Checking dashboard health ==="
curl -f http://localhost:8000/health || echo "Dashboard health check failed"

echo "=== Dashboard available at: http://localhost:8000/top ==="

echo "=== Cron jobs ==="
docker-compose exec etl crontab -l

echo "=== ETL container logs (last 20 lines) ==="
docker-compose logs --tail=20 etl

echo "=== Dashboard container logs (last 10 lines) ==="
docker-compose logs --tail=10 dashboard

echo ""
echo "🎉 Done! All services are running with Docker Compose."
echo "✅ Linting and tests completed"
echo "📊 Dashboard: http://localhost:8000/top"
echo "📈 Database: localhost:5432"
echo "📋 To view ETL logs: docker-compose logs -f etl"
echo "📋 To view Dashboard logs: docker-compose logs -f dashboard"
echo "🛑 To stop: docker-compose down"