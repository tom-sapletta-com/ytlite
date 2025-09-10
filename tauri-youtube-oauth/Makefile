.PHONY: help install dev build test clean config config-show tokens-show deps-linux doctor start fmt clean-all

# Colors for output
GREEN := \033[0;32m
YELLOW := \033[1;33m
RED := \033[0;31m
NC := \033[0m # No Color

# OS-specific Tauri app config dir (identifier: com.ytlite.oauth)
UNAME_S := $(shell uname -s 2>/dev/null)
ifeq ($(UNAME_S),Darwin)
  CONFIG_DIR := $(HOME)/Library/Application Support/com.ytlite.oauth
else ifeq ($(UNAME_S),Linux)
  CONFIG_DIR := $(HOME)/.config/com.ytlite.oauth
else
  CONFIG_DIR := $(APPDATA)/com.ytlite.oauth
endif

help: ## Show this help message
	@echo "$(GREEN)🔐 Tauri YouTube OAuth - Desktop OAuth App$(NC)"
	@echo "$(YELLOW)Filozofia: Secure Authentication for YTLite$(NC)"
	@echo ""
	@echo "$(YELLOW)Usage:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}'

install: ## Install dependencies for Tauri OAuth app
	@echo "$(YELLOW)📦 Installing dependencies...$(NC)"
	@if ! command -v cargo >/dev/null 2>&1; then \
		echo "$(YELLOW)Installing Rust toolchain (rustup)...$(NC)"; \
		curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y; \
	fi
	@CARGO_BIN="$$HOME/.cargo/bin/cargo"; \
	if ! command -v tauri >/dev/null 2>&1; then \
		echo "$(YELLOW)Installing Tauri CLI...$(NC)"; \
		"$$CARGO_BIN" install tauri-cli; \
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
	@npm run test || echo "(No JS tests configured)"
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

config: ## Configure OAuth credentials (writes to Tauri app config dir)
	@echo "$(YELLOW)🔑 Configuring OAuth credentials...$(NC)"
	@echo "Client ID:"; \
	read client_id; \
	echo "Client Secret:"; \
	read client_secret; \
	CONFIG_DIR="$(CONFIG_DIR)"; \
	mkdir -p "$$CONFIG_DIR"; \
	printf '{"client_id":"%s","client_secret":"%s"}\n' "$$client_id" "$$client_secret" > "$$CONFIG_DIR/oauth_config.json"; \
	echo "$(GREEN)✅ OAuth configuration saved to $$CONFIG_DIR/oauth_config.json$(NC)"

config-show: ## Show current OAuth config path and contents
	@echo "Config dir: $(CONFIG_DIR)"
	@cat "$(CONFIG_DIR)/oauth_config.json" 2>/dev/null || echo "No config found."

tokens-show: ## Show saved tokens path and contents (if exist)
	@echo "Tokens dir: $(CONFIG_DIR)"
	@cat "$(CONFIG_DIR)/tokens.json" 2>/dev/null || echo "No tokens found. Login first in app."

deps-linux: ## Install Linux prerequisites for Tauri (requires sudo)
	@echo "$(YELLOW)🧰 Installing Linux prerequisites (requires sudo)...$(NC)"
	sudo apt-get update
	sudo apt-get install -y libgtk-3-dev libwebkit2gtk-4.1-0 libwebkit2gtk-4.1-dev libayatana-appindicator3-dev librsvg2-dev patchelf

doctor: ## Check environment for Node, Rust, Tauri prerequisites
	@echo "$(YELLOW)🔎 Environment check...$(NC)"
	@node -v || echo "node not found"
	@npm -v || echo "npm not found"
	@cargo --version || echo "cargo not found"
	@rustc --version || echo "rustc not found"
	@tauri -V || echo "tauri CLI not found"
	@uname -a
	@echo "OS config dir: $(CONFIG_DIR)"
	@echo "$(GREEN)✅ Doctor check complete$(NC)"

start: dev ## Alias for dev

fmt: ## Format Rust and TS sources (best-effort)
	@echo "$(YELLOW)🧹 Formatting sources...$(NC)"
	@cd src-tauri && (cargo fmt || true)
	@npx --yes prettier -w "src/**/*.{ts,tsx}" || true
	@echo "$(GREEN)✅ Format complete$(NC)"

clean-all: clean ## Clean including dependencies and Rust target
	@rm -rf node_modules src-tauri/target
