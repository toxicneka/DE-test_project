#!/bin/bash

set -e

echo "=== Running linting (ruff) ==="
docker-compose exec etl ruff check scripts/ tests/

echo "=== Running unit tests (pytest) ==="
docker-compose exec etl pytest tests/ -v --cov=scripts --cov-report=term-missing

echo "✅ All checks passed!"