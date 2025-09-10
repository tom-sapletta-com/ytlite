.PHONY: help install clean generate shorts upload publish docker-build docker-run preview daily test

# Colors for output
GREEN := \033[0;32m
YELLOW := \033[1;33m
RED := \033[0;31m
NC := \033[0m # No Color

help: ## Show this help message
	@echo "$(GREEN)🎬 YTLite - YouTube Content Automation$(NC)"
	@echo "$(YELLOW)Filozofia: Simple > Complex, Consistency > Perfection$(NC)"
	@echo ""
	@echo "$(YELLOW)Usage:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}'

install: ## Install dependencies locally
	@bash scripts/install.sh

check-deps: ## Check and install missing dependencies
	@bash scripts/check-deps.sh

generate: ## Generate videos from markdown content
	bash scripts/generate.sh

shorts: ## Create YouTube Shorts from existing videos
	@bash scripts/shorts.sh

upload: ## Upload videos to YouTube
	@bash scripts/upload.sh

publish: generate shorts ## Full pipeline: generate + shorts + upload (no upload by default)
	@bash scripts/publish.sh

daily: ## Generate daily content automatically
	@bash scripts/daily.sh

# Docker commands
docker-build-base: ## Build base Docker image (heavy dependencies)
	@bash scripts/docker-build-base.sh

docker-build-app: ## Build app Docker image (light, fast rebuilds)
	@bash scripts/docker-build-app.sh

docker-build: docker-build-base docker-build-app ## Build both Docker images

docker-build-fast: ## Build only app image (assumes base exists)
	@bash scripts/docker-build-fast.sh

docker-run: ## Run with Docker Compose
	@bash scripts/docker-run.sh

docker-dev: ## Run development environment with live reload
	@bash scripts/docker-dev.sh

docker-shell: ## Open shell in Docker container
	@bash scripts/docker-shell.sh

docker-tts: ## Run TTS service for audio generation
	@bash scripts/docker-tts.sh

docker-video: ## Run video generation service
	@bash scripts/docker-video.sh

docker-upload: ## Run upload service for YouTube
	@bash scripts/docker-upload.sh

docker-all-services: ## Run all specialized services
	@bash scripts/docker-all-services.sh

# Preview and development
preview: ## Preview output locally on http://localhost:8080
	@bash scripts/preview.sh

dev-watch: ## Watch for changes and auto-generate
	@bash scripts/dev-watch.sh

automation: ## Start automation scheduler
	@bash scripts/automation.sh

# Testing and maintenance
test: ## Run tests
	@bash scripts/test.sh

stats: ## Show project statistics
	@bash scripts/stats.sh

clean: ## Clean generated files
	@bash scripts/clean.sh

validate: ## Validate generated videos with STT and analysis
	@bash scripts/validate.sh

publish-pypi: ## Publish project to PyPI
	@bash scripts/publish-pypi.sh

# Quick content creation
quick: ## Quick content from stdin (echo "content" | make quick)
	@bash scripts/quick.sh
