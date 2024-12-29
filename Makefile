# Название приложения и переменные
APP_NAME = pastebin
DOCKER_COMPOSE = docker-compose
PYTHON = python3.13

# Команды для Docker
build:
	@echo "Building Docker containers..."
	$(DOCKER_COMPOSE) up --build -d

up:
	@echo "Starting Docker containers..."
	$(DOCKER_COMPOSE) up -d

down:
	@echo "Stopping Docker containers..."
	$(DOCKER_COMPOSE) down

logs:
	@echo "Showing logs..."
	$(DOCKER_COMPOSE) logs -f

restart:
	@echo "Restarting Docker containers..."
	$(DOCKER_COMPOSE) down
	$(DOCKER_COMPOSE) up -d

# Команды для Python
venv:
	@echo "Creating virtual environment..."
	$(PYTHON) -m venv venv

install:
	@echo "Installing dependencies..."
	pip install --upgrade pip
	pip install -r requirements.txt

freeze:
	@echo "Freezing dependencies to requirements.txt..."
	pip freeze > requirements.txt

test:
	@echo "Running tests..."
	pytest

lint:
	@echo "Linting and fixing code..."
	black . || true
	isort . || true
	autoflake --in-place --remove-all-unused-imports --remove-unused-variables --recursive app/
	autopep8 --in-place --aggressive --aggressive --recursive app/
	flake8 app/ || true


BLACK=$(shell which black)
ISORT=$(shell which isort)
AUTOFLAKE=$(shell which autoflake)
FLAKE8=$(shell which flake8)

BLACK=$(shell which black)
ISORT=$(shell which isort)
AUTOFLAKE=$(shell which autoflake)
FLAKE8=$(shell which flake8)

# Укажите папки вашего проекта для проверки
PROJECT_DIRS=app tests

PROJECT_DIRS := app tests

lint2:
	@echo "Linting and fixing only project-specific files..."
	@find $(PROJECT_DIRS) -type f -name "*.py" -readable -exec chmod +r {} \; -exec chmod +w {} \; 2>/dev/null
	@find $(PROJECT_DIRS) -type f -name "*.py" -readable ! -path "*/venv/*" ! -path "*/site-packages/*" -exec black {} + || true
	@find $(PROJECT_DIRS) -type f -name "*.py" -readable ! -path "*/venv/*" ! -path "*/site-packages/*" -exec isort {} + || true
	@find $(PROJECT_DIRS) -type f -name "*.py" -readable ! -path "*/venv/*" ! -path "*/site-packages/*" -exec autoflake --in-place --remove-all-unused-imports --remove-unused-variables {} + || true
	@find $(PROJECT_DIRS) -type f -name "*.py" -readable ! -path "*/venv/*" ! -path "*/site-packages/*" -exec flake8 {} + || true

# Команды для базы данных
migrate:
	@echo "Applying database migrations..."
	$(DOCKER_COMPOSE) exec web alembic upgrade head

makemigrations:
	@echo "Generating new database migrations..."
	$(DOCKER_COMPOSE) exec web alembic revision --autogenerate -m "Migration"

# Команды для отладки
shell:
	@echo "Entering web container shell..."
	$(DOCKER_COMPOSE) exec web sh

dbshell:
	@echo "Entering database container shell..."
	$(DOCKER_COMPOSE) exec db psql -U admin -d pastebin

# Удаление артефактов
clean:
	@echo "Cleaning up..."
	rm -rf __pycache__ venv .pytest_cache .coverage

# Справка
help:
	@echo "Available commands:"
	@echo "  build            Build Docker containers"
	@echo "  up               Start Docker containers"
	@echo "  down             Stop Docker containers"
	@echo "  logs             Show logs for all containers"
	@echo "  restart          Restart Docker containers"
	@echo "  venv             Create virtual environment"
	@echo "  install          Install Python dependencies"
	@echo "  freeze           Freeze dependencies into requirements.txt"
	@echo "  test             Run tests with pytest"
	@echo "  lint             Lint the code with flake8"
	@echo "  migrate          Apply database migrations"
	@echo "  makemigrations   Generate new database migrations"
	@echo "  shell            Enter web container shell"
	@echo "  dbshell          Enter database container shell"
	@echo "  clean            Remove temporary files"
