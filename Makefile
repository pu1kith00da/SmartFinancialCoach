.PHONY: help install run test clean migrate db-up db-down docker-up docker-down

help:
	@echo "Smart Financial Coach - Available Commands"
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make install       - Install Python dependencies"
	@echo "  make db-up         - Start PostgreSQL and Redis with Docker"
	@echo ""
	@echo "Development:"
	@echo "  make run           - Run the FastAPI development server"
	@echo "  make test          - Run all tests"
	@echo "  make migrate       - Run database migrations"
	@echo ""
	@echo "Database:"
	@echo "  make db-shell      - Open PostgreSQL shell"
	@echo "  make db-reset      - Reset database (drop all tables)"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-up     - Start all Docker services"
	@echo "  make docker-down   - Stop all Docker services"
	@echo "  make docker-logs   - View Docker logs"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean         - Remove cache files and build artifacts"

install:
	cd backend && python3 -m venv venv
	cd backend && . venv/bin/activate && pip install -r requirements.txt

run:
	cd backend && . venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	cd backend && . venv/bin/activate && pytest tests/ -v

test-cov:
	cd backend && . venv/bin/activate && pytest tests/ --cov=app --cov-report=html

migrate:
	cd backend && . venv/bin/activate && alembic upgrade head

migrate-create:
	cd backend && . venv/bin/activate && alembic revision --autogenerate -m "$(msg)"

migrate-down:
	cd backend && . venv/bin/activate && alembic downgrade -1

db-up:
	docker-compose up -d postgres redis

db-down:
	docker-compose stop postgres redis

db-shell:
	docker-compose exec postgres psql -U fincoach -d fincoach

db-reset:
	docker-compose exec postgres psql -U fincoach -d fincoach -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
	make migrate

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

docker-rebuild:
	docker-compose down
	docker-compose build --no-cache
	docker-compose up -d

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".coverage" -delete
	find . -type d -name "htmlcov" -exec rm -rf {} +

format:
	cd backend && . venv/bin/activate && black app/ tests/
	cd backend && . venv/bin/activate && isort app/ tests/

lint:
	cd backend && . venv/bin/activate && flake8 app/ tests/
	cd backend && . venv/bin/activate && mypy app/

dev: db-up migrate run

.DEFAULT_GOAL := help
