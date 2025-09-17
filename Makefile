.PHONY: help setup install test lint format clean start stop validate init docker-build docker-run

# Default target
help:
	@echo "AI Cold Calling Agent - Available Commands:"
	@echo ""
	@echo "Setup and Installation:"
	@echo "  setup        - Run initial setup script"
	@echo "  install      - Install dependencies"
	@echo "  init         - Initialize configuration"
	@echo ""
	@echo "Development:"
	@echo "  test         - Run tests"
	@echo "  lint         - Run linting"
	@echo "  format       - Format code"
	@echo "  validate     - Validate configuration"
	@echo ""
	@echo "Application:"
	@echo "  start        - Start the agent"
	@echo "  stop         - Stop the agent"
	@echo ""
	@echo "Docker:"
	@echo "  docker-build - Build Docker image"
	@echo "  docker-run   - Run with Docker Compose"
	@echo ""
	@echo "Maintenance:"
	@echo "  clean        - Clean temporary files"

# Setup and installation
setup:
	@echo "Running setup script..."
	./setup.sh

install:
	@echo "Installing dependencies..."
	pip install -r requirements.txt

init:
	@echo "Initializing configuration..."
	python3 run.py init

# Development
test:
	@echo "Running tests..."
	python3 -m pytest tests/ -v

lint:
	@echo "Running linting..."
	python3 -m flake8 src/ tests/ --max-line-length=100
	python3 -m mypy src/ --ignore-missing-imports

format:
	@echo "Formatting code..."
	python3 -m black src/ tests/ examples/ --line-length=100

validate:
	@echo "Validating configuration..."
	python3 run.py validate

# Application
start:
	@echo "Starting AI Cold Calling Agent..."
	python3 run.py start

stop:
	@echo "Stopping AI Cold Calling Agent..."
	pkill -f "python3 run.py start" || true

# Docker
docker-build:
	@echo "Building Docker image..."
	docker build -t aiagent:latest .

docker-run:
	@echo "Running with Docker Compose..."
	docker-compose up -d

docker-stop:
	@echo "Stopping Docker containers..."
	docker-compose down

# Maintenance
clean:
	@echo "Cleaning temporary files..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf build/ dist/ .coverage htmlcov/

# Database
db-init:
	@echo "Initializing database..."
	python3 -c "import sys; sys.path.insert(0, 'src'); from src.database import DatabaseManager; from src.config import create_config_manager; config = create_config_manager(); db = DatabaseManager(config.get_database_url()); db.create_tables()"

db-reset:
	@echo "Resetting database..."
	@echo "WARNING: This will delete all data!"
	@read -p "Are you sure? [y/N] " confirm && [ "$$confirm" = "y" ] || exit 1
	python3 -c "import sys; sys.path.insert(0, 'src'); from src.database import DatabaseManager; from src.config import create_config_manager; config = create_config_manager(); db = DatabaseManager(config.get_database_url()); from src.database.models import Base; Base.metadata.drop_all(db.engine); Base.metadata.create_all(db.engine)"

# Development server
dev:
	@echo "Starting development server..."
	python3 run.py start --dev

# Package
package:
	@echo "Building package..."
	python3 -m build

# Install package in development mode
dev-install:
	@echo "Installing in development mode..."
	pip install -e .