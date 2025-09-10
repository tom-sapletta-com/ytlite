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
	python3 src/youtube_uploader.py --batch output/
	@echo "$(GREEN)✅ Upload complete$(NC)"

publish: generate shorts ## Full pipeline: generate + shorts + upload (no upload by default)
	@echo "$(GREEN)✅ Content ready! Use 'make upload' to publish$(NC)"

daily: ## Generate daily content automatically
	@echo "$(YELLOW)🤖 Generating daily content...$(NC)"
	python3 src/ytlite.py daily
	@echo "$(GREEN)✅ Daily content ready$(NC)"

# Docker commands
docker-build: ## Build Docker image
	docker build -t ytlite:latest .

docker-run: docker-build ## Run generation in Docker
	docker-compose --profile generator up ytlite

docker-shell: ## Shell into container for debugging
	docker run -it --rm -v $(PWD):/app ytlite:latest bash

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
