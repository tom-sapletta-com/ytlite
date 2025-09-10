.PHONY: help install dev build test clean config

# Colors for output
GREEN := \033[0;32m
YELLOW := \033[1;33m
RED := \033[0;31m
NC := \033[0m # No Color

help: ## Show this help message
	@echo "$(GREEN)🔐 Tauri YouTube OAuth - Desktop OAuth App$(NC)"
	@echo "$(YELLOW)Filozofia: Secure Authentication for YTLite$(NC)"
	@echo ""
	@echo "$(YELLOW)Usage:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}'

install: ## Install dependencies for Tauri OAuth app
	@echo "$(YELLOW)📦 Installing dependencies...$(NC)"
	@if ! command -v cargo &> /dev/null; then \
		echo "$(RED)Error: Rust and Cargo are not installed. Installing...$(NC)"; \
		curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y; \
		source $$HOME/.cargo/env; \
	fi
	@if ! command -v tauri-cli &> /dev/null; then \
		echo "$(YELLOW)Installing Tauri CLI...$(NC)"; \
		cargo install tauri-cli; \
	fi
	@echo "$(YELLOW)Installing Node.js dependencies...$(NC)"
	npm install
	@echo "$(GREEN)✅ Dependencies installed$(NC)"

dev: ## Run Tauri app in development mode with hot reload
	@echo "$(YELLOW)🚀 Starting Tauri app in development mode...$(NC)"
	npm run dev
	@echo "$(GREEN)✅ Development mode started$(NC)"

build: ## Build Tauri app for production
	@echo "$(YELLOW)🏗️ Building Tauri app for production...$(NC)"
	npm run build
	@echo "$(GREEN)✅ Build complete$(NC)"

test: ## Run tests for Tauri app
	@echo "$(YELLOW)🧪 Running tests...$(NC)"
	npm run test
	@if [ -d "src-tauri" ]; then \
		echo "$(YELLOW)Running Rust tests...$(NC)"; \
		cd src-tauri && cargo test; \
	fi
	@echo "$(GREEN)✅ Tests complete$(NC)"

clean: ## Clean build artifacts and dependencies
	@echo "$(YELLOW)🧹 Cleaning build artifacts and dependencies...$(NC)"
	rm -rf node_modules
	rm -rf dist
	if [ -d "src-tauri" ]; then \
		cd src-tauri && cargo clean; \
	fi
	@echo "$(GREEN)✅ Cleaned$(NC)"

config: ## Configure OAuth credentials for the app
	@echo "$(YELLOW)🔑 Configuring OAuth credentials...$(NC)"
	@echo "Please enter your Google OAuth Client ID:"
	@read client_id; \
		echo "Please enter your Google OAuth Client Secret:"; \
		read client_secret; \
		echo "{\"client_id\": \"$$client_id\", \"client_secret\": \"$$client_secret\"}" > oauth_config.json; \
		echo "$(GREEN)✅ OAuth configuration saved to oauth_config.json$(NC)"
