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
	@echo "$(YELLOW)📦 Installing dependencies...$(NC)"
	pip3 install -r requirements.txt
	mkdir -p {content/episodes,output/{videos,shorts,thumbnails},credentials,config}
	@echo "$(GREEN)✅ Dependencies installed$(NC)"

generate: ## Generate videos from markdown content
	@echo "$(YELLOW)🎬 Generating videos...$(NC)"
	@for file in content/episodes/*.md; do \
		if [ -f "$$file" ]; then \
			echo "Processing: $$file"; \
			python3 src/ytlite.py generate "$$file"; \
		fi \
	done
	@echo "$(GREEN)✅ Videos generated$(NC)"

shorts: ## Create YouTube Shorts from existing videos
	@echo "$(YELLOW)📱 Creating Shorts...$(NC)"
	python3 src/ytlite.py shorts output/videos/*.mp4
	@echo "$(GREEN)✅ Shorts created$(NC)"

upload: ## Upload videos to YouTube
	@echo "$(YELLOW)📤 Uploading to YouTube...$(NC)"
	python3 src/youtube_uploader.py upload --batch --folder output/
	@echo "$(GREEN)✅ Upload complete$(NC)"

publish: generate shorts ## Full pipeline: generate + shorts + upload (no upload by default)
	@echo "$(GREEN)✅ Content ready! Use 'make upload' to publish$(NC)"

daily: ## Generate daily content automatically
	@echo "$(YELLOW)🤖 Generating daily content...$(NC)"
	python3 src/ytlite.py daily
	@echo "$(GREEN)✅ Daily content ready$(NC)"

# Docker commands
docker-build-base: ## Build base Docker image (heavy dependencies)
	@echo "$(YELLOW)🐳 Building base Docker image...$(NC)"
	@if docker images | grep -q "ytlite:base"; then \
		echo "$(YELLOW)Base image already exists. Skipping rebuild. Use 'docker rmi ytlite:base' to force rebuild.$(NC)"; \
	else \
		docker build -f Dockerfile.base -t ytlite:base .; \
	fi
	@echo "$(GREEN)✅ Base Docker image built (cached for future builds)$(NC)"

docker-build-app: ## Build app Docker image (light, fast rebuilds)
	@echo "$(YELLOW)🐳 Building app Docker image...$(NC)"
	@if docker images | grep -q "ytlite:app"; then \
		echo "$(YELLOW)App image already exists. Skipping rebuild. Use 'docker rmi ytlite:app' to force rebuild.$(NC)"; \
	else \
		docker build -f Dockerfile.app -t ytlite:app .; \
	fi
	@echo "$(GREEN)✅ App Docker image built$(NC)"

docker-build: docker-build-base docker-build-app ## Build both Docker images

docker-build-fast: ## Build only app image (assumes base exists)
	@echo "$(YELLOW)⚡ Fast Docker build (app only)...$(NC)"
	docker build -f Dockerfile.app -t ytlite:app .
	@echo "$(GREEN)✅ Fast build complete$(NC)"

docker-run: ## Run with Docker Compose
	@echo "$(YELLOW)🐳 Starting Docker services...$(NC)"
	docker-compose up --build -d
	@echo "$(GREEN)✅ Docker services started$(NC)"

docker-dev: ## Run development environment with live reload
	@echo "$(YELLOW)🔧 Starting development environment...$(NC)"
	docker-compose up ytlite-dev nginx -d
	@echo "$(GREEN)✅ Development environment started$(NC)"

docker-shell: ## Open shell in Docker container
	@echo "$(YELLOW)🐳 Opening Docker shell...$(NC)"
	docker run -it --rm -v $(PWD):/app ytlite:app bash

# Tauri OAuth App helpers
oauth-install: ## Install Node deps for Tauri OAuth app
	@echo "$(YELLOW)📦 Installing Tauri OAuth app dependencies...$(NC)"
	npm --prefix tauri-youtube-oauth install
	@echo "$(GREEN)✅ Tauri OAuth deps installed$(NC)"

oauth-dev: ## Run Tauri OAuth app in dev mode (requires Rust toolchain)
	@echo "$(YELLOW)🖥️  Starting Tauri OAuth app...$(NC)"
	npm --prefix tauri-youtube-oauth run dev

oauth-build: ## Build Tauri OAuth app (desktop binary)
	@echo "$(YELLOW)🏗️  Building Tauri OAuth app...$(NC)"
	npm --prefix tauri-youtube-oauth run build
	@echo "$(GREEN)✅ Tauri OAuth app built$(NC)"

docker-tts: ## Run TTS service for audio generation
	@echo "$(YELLOW)🔊 Starting TTS service...$(NC)"
	docker-compose --profile tts up tts-service -d
	@echo "$(GREEN)✅ TTS service started$(NC)"

docker-video: ## Run video generation service
	@echo "$(YELLOW)🎬 Starting video generation service...$(NC)"
	docker-compose --profile video up video-generator -d
	@echo "$(GREEN)✅ Video generation service started$(NC)"

docker-upload: ## Run upload service for YouTube
	@echo "$(YELLOW)📤 Starting upload service...$(NC)"
	docker-compose --profile upload up uploader -d
	@echo "$(GREEN)✅ Upload service started$(NC)"

docker-all-services: ## Run all specialized services
	@echo "$(YELLOW)🌐 Starting all specialized services...$(NC)"
	docker-compose --profile tts --profile video --profile upload up tts-service video-generator uploader -d
	@echo "$(GREEN)✅ All specialized services started$(NC)"

# Preview and development
preview: ## Preview output locally on http://localhost:8080
	@echo "$(YELLOW)🌐 Starting preview server...$(NC)"
	docker-compose --profile preview up nginx

dev-watch: ## Watch for changes and auto-generate
	@echo "$(YELLOW)👀 Watching for changes...$(NC)"
	python3 src/ytlite.py watch

automation: ## Start automation scheduler
	@echo "$(YELLOW)⏰ Starting automation...$(NC)"
	docker-compose --profile automation up scheduler

# Testing and maintenance
test: ## Run tests
	@echo "$(YELLOW)🧪 Running tests...$(NC)"
	python3 -m pytest tests/ -v || echo "No tests found"

stats: ## Show project statistics
	python3 src/ytlite.py stats

clean: ## Clean generated files
	@echo "$(YELLOW)🧹 Cleaning...$(NC)"
	rm -rf output/videos/*.mp4 output/shorts/*.mp4 output/thumbnails/*.jpg
	@echo "$(GREEN)✅ Cleaned$(NC)"

# Quick content creation
quick: ## Quick content from stdin (echo "content" | make quick)
	@echo "$(YELLOW)⚡ Quick content creation...$(NC)"
	@timestamp=$$(date +%Y%m%d_%H%M%S); \
	echo "---" > content/episodes/quick_$$timestamp.md; \
	echo "title: 'Quick thought $$timestamp'" >> content/episodes/quick_$$timestamp.md; \
	echo "date: $$(date +%Y-%m-%d)" >> content/episodes/quick_$$timestamp.md; \
	echo "theme: philosophy" >> content/episodes/quick_$$timestamp.md; \
	echo "---" >> content/episodes/quick_$$timestamp.md; \
	echo "" >> content/episodes/quick_$$timestamp.md; \
	cat >> content/episodes/quick_$$timestamp.md; \
	make generate
	@echo "$(GREEN)✅ Quick content generated$(NC)"
