.PHONY: help install clean generate shorts upload upload-project publish docker-build docker-run preview daily test gui

# Colors for output
GREEN := \033[0;32m
YELLOW := \033[1;33m
RED := \033[0;31m
NC := \033[0m # No Color

# ==============================================================================
# HELP
# ==============================================================================
help: ## Show this help message
	@echo "$(GREEN)🎬 YTLite - YouTube Content Automation$(NC)"
	@echo "$(YELLOW)Filozofia: Simple > Complex, Consistency > Perfection$(NC)"
	@echo ""
	@echo "$(YELLOW)Usage:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}'

# ==============================================================================
# LOCAL WORKFLOW
# ==============================================================================
install: ## Install/update local dependencies
	bash scripts/install.sh
	$(MAKE) validate

check-deps: ## Check and install missing OS dependencies
	bash scripts/check-deps.sh

generate: ## Generate videos from markdown content
	bash scripts/generate.sh

shorts: ## Create YouTube Shorts from existing videos
	bash scripts/shorts.sh

upload: ## Upload generated videos to YouTube
	@bash scripts/upload.sh

upload-project: ## Upload a single project's video (usage: make upload-project PROJECT=<name> [PRIVACY=unlisted])
	@python3 -u src/youtube_uploader.py upload_project --project $(PROJECT) $(if $(PRIVACY),--privacy $(PRIVACY),)

publish: generate shorts ## Full pipeline: generate + shorts + upload (no upload by default)
	bash scripts/publish.sh

daily: ## Generate daily content automatically
	bash scripts/daily.sh

# ==============================================================================
# DOCKER WORKFLOW
# ==============================================================================
docker-build: ## Build all necessary Docker images (app, tauri, etc.)
	docker-compose --profile app --profile tauri build

docker-up: ## Start all services in the background (app, preview, tauri)
	docker-compose --profile app --profile preview --profile tauri up -d

docker-down: ## Stop and remove all running containers
	docker-compose down

docker-logs: ## Follow logs from all running services
	docker-compose logs -f

docker-shell: ## Open a shell in the main app container
	docker-compose exec ytlite-app bash

# --- Tauri Specific Docker Commands ---
tauri-shell: ## Open a shell in the Tauri dev container
	docker-compose exec tauri-dev bash

tauri-build: ## Build the Tauri application inside Docker
	docker-compose exec tauri-dev bash -c "cd src-tauri && cargo build --release"

tauri-test: ## Run all Tauri tests (E2E and contract)
	make tauri-test-e2e
	make tauri-test-contract

tauri-check: ## Check Rust code in Tauri container
	docker-compose exec tauri-dev bash -c "cd src-tauri && cargo check"

tauri-test-e2e: ## Run Tauri E2E tests in Docker
	docker-compose exec tauri-dev npm run test:e2e

tauri-test-contract: ## Run Tauri contract tests in Docker
	docker-compose exec tauri-dev bash -c "cd src-tauri && cargo test"

# ==============================================================================
# DEVELOPMENT & MAINTENANCE
# ==============================================================================
preview: ## Preview output locally on http://localhost:8080
	bash scripts/preview.sh

dev-watch: ## Watch for changes and auto-generate (local)
	@bash scripts/dev-watch.sh

automation: ## Start automation scheduler (local)
	@bash scripts/automation.sh

test: ## Run local Python tests
	bash scripts/test.sh

stats: ## Show project statistics
	@bash scripts/stats.sh

clean: ## Clean generated files
	@bash scripts/clean.sh

validate: ## Validate generated videos with STT and analysis, and check dependencies
	bash scripts/check-deps.sh
	bash scripts/validate.sh

# Lightweight app smoke test: deps + generate sample + verify packaging
validate-app: ## Validate application health (deps + smoke generate + project packaging)
	bash scripts/validate-app.sh

# Lightweight data integrity validation of output/projects/
validate-data: ## Validate generated data integrity (projects folders and required files)
	bash scripts/validate-data.sh

publish-pypi: ## Publish project to PyPI
	@bash scripts/publish-pypi.sh

# Quick content creation
quick: ## Quick content from stdin (echo "content" | make quick)
	@bash scripts/quick.sh

gui: ## Run Web GUI (Flask) on http://localhost:5000
	@bash scripts/gui.sh
