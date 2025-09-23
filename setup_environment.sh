#!/bin/bash
# Setup script for YTLite development environment

set -e

echo "🚀 Setting up YTLite development environment..."

# Check Python version
PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "🐍 Using Python $PYTHON_VERSION"

# Create and activate virtual environment
echo "🔧 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
echo "🔄 Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Install development dependencies
echo "🔧 Installing development dependencies..."
pip install -e .

# Check FFmpeg
echo "🎬 Checking FFmpeg installation..."
if ! command -v ffmpeg &> /dev/null; then
    echo "❌ FFmpeg is not installed. Installing..."
    
    # Try different package managers
    if command -v apt-get &> /dev/null; then
        sudo apt-get update && sudo apt-get install -y ffmpeg
    elif command -v brew &> /dev/null; then
        brew install ffmpeg
    elif command -v conda &> /dev/null; then
        conda install -y -c conda-forge ffmpeg
    else
        echo "⚠️  Could not install FFmpeg automatically. Please install it manually:"
        echo "   Ubuntu/Debian: sudo apt-get install ffmpeg"
        echo "   macOS: brew install ffmpeg"
        echo "   Windows: Download from https://ffmpeg.org/download.html"
        exit 1
    fi
else
    echo "✅ FFmpeg is already installed"
fi

# Verify FFmpeg installation
echo "🔍 Verifying FFmpeg installation..."
ffmpeg -version | head -n 1

# Run tests
echo "🧪 Running tests..."
python -m pytest tests/ -v

echo "✨ Setup complete! Activate the virtual environment with:"
echo "   source venv/bin/activate"
echo ""
echo "To start the development server, run:"
echo "   make run-server"
