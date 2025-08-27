# Circuit Simulation Learning Environment
# Convenient commands for development and learning

.PHONY: help learn learn-quick test-sim build-container stop clean

help:  ## Show this help message
	@echo "🎓 Circuit Simulation Learning Environment"
	@echo "=========================================="
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "🐳 Docker Required: All simulation runs in containerized environment"
	@echo "📚 Learning Path: Start with track1_dc_analysis/module_1.1_dc_basics/"

learn: build-container  ## Launch full interactive learning environment (recommended)
	@echo "🚀 Starting Interactive Circuit Learning Environment..."
	./learn.sh

learn-quick:  ## Quick launch (assumes container exists)
	@echo "⚡ Quick launching learning environment..."
	./quick-learn.sh

test-sim:  ## Test simulation backend in Docker
	@echo "🧪 Testing simulation backend..."
	@docker exec circuit-sim python test_interactive_learning.py || \
	 docker run --rm -v "$(PWD):/workspace" circuit-simulation:latest python test_interactive_learning.py

build-container:  ## Build Docker container with simulation backend
	@echo "🔨 Building simulation container..."
	@docker build -f deployment/Dockerfile -t circuit-simulation:latest . --quiet
	@echo "✅ Container built successfully"

stop:  ## Stop learning environment
	@echo "⏹️ Stopping learning environment..."
	@docker stop circuit-sim circuit-sim-learn > /dev/null 2>&1 || true
	@echo "✅ Stopped"

clean: stop  ## Clean up containers and images
	@echo "🧹 Cleaning up containers and images..."
	@docker rm -f circuit-sim circuit-sim-learn > /dev/null 2>&1 || true
	@docker rmi circuit-simulation:latest > /dev/null 2>&1 || true
	@echo "✅ Cleanup complete"

dev:  ## Start development environment (local)
	@echo "💻 Starting local development environment..."
	@echo "⚠️ Note: Simulation will show demo mode (Docker required for real simulation)"
	uv run jupyter lab docs/learning_modules/

# Development shortcuts
install:  ## Install local dependencies
	uv install --extra interactive

format:  ## Format code
	uv run black src/ tests/
	uv run ruff check src/ tests/ --fix

lint:  ## Check code quality
	uv run ruff check src/ tests/
	uv run mypy src/ --strict

test:  ## Run tests locally
	uv run pytest -v

test-docker:  ## Run tests in Docker
	docker run --rm -v "$(PWD):/workspace" circuit-simulation:latest python -m pytest -v