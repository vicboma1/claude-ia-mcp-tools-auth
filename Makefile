.PHONY: help install dev-install run-auth run-mcp test test-auth test-mcp test-coverage lint format clean

help:
	@echo "MCP Tools with OAuth Authentication - Available commands:"
	@echo ""
	@echo "Setup:"
	@echo "  make install       - Install dependencies"
	@echo "  make dev-install   - Install dependencies including dev tools"
	@echo ""
	@echo "Running:"
	@echo "  make run-auth      - Run authentication server (http://localhost:5000)"
	@echo "  make run-mcp       - Run MCP server"
	@echo ""
	@echo "Testing:"
	@echo "  make test          - Run all tests"
	@echo "  make test-auth     - Run authentication tests only"
	@echo "  make test-mcp      - Run MCP server tests only"
	@echo "  make test-service  - Run service tests only"
	@echo "  make test-coverage - Run tests with coverage report"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint          - Run linter (ruff)"
	@echo "  make format        - Format code with ruff"
	@echo "  make clean         - Clean up generated files"

install:
	pip install -r requirements.txt

dev-install:
	pip install -r requirements.txt
	pip install -e ".[dev]"

run-auth:
	python -m src.example.http.auth_server

run-mcp:
	python -m src.example.mcp.server

test:
	pytest -v

test-auth:
	pytest -v tests/test_auth.py

test-mcp:
	pytest -v tests/test_mcp_server.py

test-service:
	pytest -v tests/test_service.py

test-coverage:
	pytest -v --cov=src --cov-report=html --cov-report=term

lint:
	ruff check src tests

format:
	ruff format src tests

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
	find . -type d -name .mypy_cache -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf build dist *.egg-info .coverage htmlcov .ruff_cache
