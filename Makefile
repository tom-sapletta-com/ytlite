.PHONY: help install clean generate shorts upload upload-project publish docker-build docker-run preview daily test test-e2e gui logs logs-follow wordpress-test example-project

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

publish: ## Full pipeline: generate + shorts (upload is manual via `make upload`)
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

stats: ## Show project statistics
	@bash scripts/stats.sh

clean: ## Clean generated files
	@bash scripts/clean.sh

# Lightweight app smoke test: deps + generate sample + verify packaging
validate-app: ## Validate application health (deps + smoke generate + project packaging)
	bash scripts/validate-app.sh

# Lightweight data integrity validation of output/projects/
validate-data: ## Validate generated data integrity (projects folders and required files)
	bash scripts/validate-data.sh

# ==============================================================================
# VALIDATION & TESTING
# ==============================================================================
validate: ## Validate generated data and app setup
	bash scripts/validate.sh || { echo "$(YELLOW)Validation completed with non-critical errors. Continuing...$(NC)"; exit 0; }

test-data: ## Test project folders, media, and SVG files for errors and remove faulty files
	@echo "$(YELLOW)Testing project data for errors...$(NC)"
	/home/tom/github/tom-sapletta-com/ytlite/venv/bin/python3 /home/tom/github/tom-sapletta-com/ytlite/src/test_data_validator.py test_data --remove-faulty
	@echo "$(GREEN)✓ Project data testing completed$(NC)"

test: ## Run automated tests
	bash scripts/test.sh

test-e2e: ## Run E2E pytest suite quietly  
	pytest -q

# ==============================================================================
# PUBLISHING
# ==============================================================================
publish-pypi: ## Publish project to PyPI
	@bash scripts/publish-pypi.sh

# Quick content creation
quick: ## Quick content from stdin (echo "content" | make quick)
	@bash scripts/quick.sh

gui: ## Run the new, refactored Web GUI
	@echo "$(GREEN)🚀 Starting New YTLite Web GUI$(NC)"
	@python3 run_new_gui.py

gui-normal: ## Run the Web GUI with Edge TTS (FAST_TEST=0)
	@echo "$(GREEN)🚀 Starting YTLite Web GUI (Edge TTS)$(NC)"
	@YTLITE_FAST_TEST=0 python3 run_new_gui.py

gui-fasttest: ## Run the Web GUI in FAST_TEST mode (tone audio)
	@echo "$(YELLOW)⚡ Starting YTLite Web GUI in FAST_TEST mode (tone audio)$(NC)"
	@YTLITE_FAST_TEST=1 python3 run_new_gui.py

stop: ## Stop all running servers and processes
	@echo "$(YELLOW)Stopping all servers and processes...$(NC)"
	-@pkill -f "python3.*web_gui" 2>/dev/null
	-@pkill -f "python3.*minimal_web_gui" 2>/dev/null
	-@pkill -f "python3.*simple_test_server" 2>/dev/null
	-@pkill -f "python3 -m http.server" 2>/dev/null
	-@pkill -f "python3.*-c.*Flask" 2>/dev/null
	-@lsof -ti:5000 | xargs -r kill -9 2>/dev/null
	-@lsof -ti:8080 | xargs -r kill -9 2>/dev/null
	-@lsof -ti:5000 | xargs -r kill -SIGKILL 2>/dev/null
	@echo "$(GREEN)✅ All servers stopped$(NC)"

logs: ## Show last 200 lines of logs/ytlite.log
	@tail -n 200 logs/ytlite.log || echo "No logs yet"

logs-follow: ## Follow logs/ytlite.log
	@tail -f logs/ytlite.log || echo "No logs yet"

# New targets for validation
validate-app-report:
	@echo "Validating ytlite application setup and dependencies..."
	@python3 -m src.validator
	@echo "App validation complete. Check reports in the 'reports' directory."

validate-data-report:
	@echo "Validating ytlite data integrity..."
	@python3 -m src.validator
	@echo "Data validation complete. Check reports in the 'reports' directory."
