TARGET_LIST=$(shell egrep -o ^[a-zA-Z_-]+: $(MAKEFILE_LIST) | sed 's/://')
.PHONY: $(TARGET_LIST)
.DEFAULT_GOAL := help

# --------------------------------------
# Tasks
# --------------------------------------
help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

env-up-all: ## Start the all services with docker compose
	@docker compose up --build -d

env-up-app: ## Start the backend service with docker compose
	@docker compose up --build app

env-up-app-d: ## Start the backend service with docker compose in detached mode
	@docker compose up --build -d app

# env-up-db: ## Start the platform database service with docker compose (deprecated)
# 	@docker compose up --build -d app-db

env-down: ## Stop the all services with docker compose
	@docker compose --profile test down

env-down-app: ## Stop the backend service with docker compose
	@docker compose stop app

env-reload-all: ## Reload the all services with docker compose
	@docker compose --profile test down && \
	docker compose up --build -d

env-reload-app: ## Reload the backend service with docker compose
	@docker compose stop app && \
	docker compose up --build app

env-reload-app-d: ## Reload the backend service with docker compose in detached mode
	@docker compose stop app && \
	docker compose up --build -d app

env-down-v: ## Stop the all services with docker compose and remove volumes
	@docker compose --profile test down -v

# --------------------------------------
# Test Client
# --------------------------------------
env-up-test-client: ## Start the test client container
	@docker compose --profile test up -d test-client

env-down-test-client: ## Stop the test client container
	@docker compose stop test-client

exec-bash-test-client: ## Open a bash shell in the test client container
	@docker compose exec test-client bash

# --------------------------------------
# Database Migration (deprecated - stateless server)
# --------------------------------------
# db-migration: ## Apply the migration scripts
# 	@alembic upgrade head

# db-rev-generate: ## Generate a new migration script
# 	@if [ -z "$(MSG)" ]; then \
# 		echo "ERROR: マイグレーションメッセージを指定してください。使用例: make db-rev-generate MSG=\"add example_col column to example_table\""; \
# 		exit 1; \
# 	fi
# 	alembic revision -m "$(MSG)"

# db-rev-downgrade: ## Downgrade the database to a specific revision
# 	@if [ -z "$(REV)" ]; then \
# 		echo "ERROR: リビジョンを指定してください。使用例: make db-rev-downgrade REV=1234567890"; \
# 		exit 1; \
# 	fi
# 	alembic downgrade "$(REV)"

# env-db-migration: ## Apply the migration scripts in the container
# 	@docker compose run --rm app make db-migration

run-local: ## Run the backend application in host machine
	@uvicorn app.main:app --reload

app-logs: ## Show the logs of the backend service
	@docker compose logs -f app

exec-bash: ## Open a bash shell in the backend container
	@docker compose exec app bash

# exec-bash-db: ## Open a bash shell in the admin database container (deprecated)
# 	@docker compose exec app-db bash

pkg-install-local: ## Install the Python packages locally
	@if [ ! -d ".venv" ]; then \
		echo "Creating virtual environment..."; \
		uv venv; \
	fi && \
	source .venv/bin/activate && \
	uv sync

check-format: ## Check the code formatting
	@ruff check . && \
	ruff format --check .

run-format: ## Run the code formatting
	@ruff check --fix . && \
	ruff format .

run-format-unsafe-fix: ## Run the code formatting (unsafe fix)
	@ruff check --fix  --unsafe-fixes . && \
	ruff format .

test: ## Run the tests
	@pytest -s --cov=app --cov-report=term-missing
