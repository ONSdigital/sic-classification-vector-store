.PHONY: all
all: ## Show the available make targets.
	@echo "Usage: make <target>"
	@echo ""
	@echo "Targets:"
	@fgrep "##" Makefile | fgrep -v fgrep

.PHONY: clean
clean: ## Clean the temporary files.
	rm -rf .mypy_cache
	rm -rf .ruff_cache	

# Make does not like interpreting : in the target name, so we use a variable
API_CMD=poetry run uvicorn sic_classification_vector_store.api.main:app --host 0.0.0.0 --port 8088 --reload

.PHONY: run-vector-store
run-vector-store: ## Run the vectore store and API
	$(API_CMD)

.PHONY: run-docs
run-docs: ## Run the mkdocs
	poetry run mkdocs serve

.PHONY: check-python
check-python: ## Format the python code (auto fix)
	poetry run isort . --verbose
	poetry run black .
	poetry run ruff check . --fix
	poetry run mypy --follow-untyped-imports  . 
	poetry run pylint --verbose .
	poetry run bandit -r src/sic_classification_vector_store/api src/sic_classification_vector_store/utils

.PHONY: check-python-nofix
check-python-nofix: ## Format the python code (no fix)
	poetry run isort . --check --verbose
	poetry run black . --check
	poetry run ruff check .
	poetry run mypy --follow-untyped-imports  . 
	poetry run pylint --verbose .
	poetry run bandit -r src/sic_classification_vector_store/api src/sic_classification_vector_store/utils

.PHONY: black
black: ## Run black
	poetry run black .

.PHONY: unit-tests
unit-tests: ## Run the example unit tests
	poetry run pytest -m utils --cov=utils --cov-report=term-missing --cov-fail-under=80 --cov-config=.coveragerc

.PHONY: api-tests
api-tests: ## Run the example API tests
	poetry run pytest -m api --cov=api --cov-report=term-missing --cov-fail-under=80 --cov-config=.coveragerc

.PHONY: all-tests
all-tests:
	poetry run pytest  --cov=. --cov-report=term-missing --cov-fail-under=80 --cov-config=.coveragerc

.PHONY: install	
install: ## Install the dependencies
	poetry install --only main --no-root

.PHONY: install-dev
install-dev: ## Install the dev dependencies
	poetry install --no-root

.PHONY: colima-start
colima-start: ## Start Colima
	colima start --cpu 2 --memory 4 --disk 100

.PHONY: colima-stop
colima-stop: ## Stop Colima
	colima stop

.PHONY: docker-image
docker-image: ## Build the Docker image
	docker build -t vector-store -f DOCKERFILE .

.PHONY: run-docker-image
run-docker-image: ## Run the Docker image
	docker run -p 8088:8088 vector-store

.PHONY: docker-clean
docker-clean: ## Clean Docker resources
	DOCKER_HOST="unix://${HOME}/.colima/default/docker.sock" docker system prune -f

.PHONY: colima-status
colima-status: ## Check Colima status
	colima status
