#!/bin/bash
# YTLite Installation Script

set -e

echo "🚀 YTLite Installation"
echo "======================"

# Check Python version
python_version=$(python3 --version 2>&1 | grep -Po '(?<=Python )\d+\.\d+')
required_version="3.9"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then 
    echo "❌ Python $required_version+ required (you have $python_version)"
    exit 1
fi

# Check for ffmpeg
if ! command -v ffmpeg &> /dev/null; then
    echo "📦 Installing ffmpeg..."
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        sudo apt-get update && sudo apt-get install -y ffmpeg
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        brew install ffmpeg
    else
        echo "❌ Please install ffmpeg manually"
        exit 1
    fi
fi

# Create virtual environment
echo "🐍 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install package
echo "📦 Installing YTLite..."
pip install --upgrade pip
pip install -r requirements.txt

# Create directory structure
echo "📁 Creating directories..."
mkdir -p {content/episodes,output/{videos,shorts,thumbnails},credentials,config}

# Copy environment template
echo "⚙️ Setting up configuration..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "📝 Please edit .env with your API keys"
fi

# Create sample content
if [ ! -f content/episodes/sample.md ]; then
    echo "📝 Creating sample content..."
    cat > content/episodes/sample.md << 'EOF'
---
title: "Welcome to YTLite"
date: 2025-01-15
theme: tech
tags: [welcome, tutorial]
---

Welcome to YTLite, the minimalist YouTube automation tool.

Creating content has never been easier.

Just write markdown, and let the automation handle the rest.
EOF
fi

echo ""
echo "✅ Installation complete!"
echo ""
echo "📚 Quick Start:"
echo "  1. Activate environment: source venv/bin/activate"
echo "  2. Edit configuration: nano .env"
echo "  3. Generate sample video: make generate"
echo "  4. Preview results: make preview"
echo ""
echo "🎬 Happy content creating!"
