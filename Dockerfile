# Multi-stage build for better performance
# Stage 1: Base image with system dependencies (cache-friendly)
FROM python:3.11-slim AS base

# Install system dependencies (this layer will be cached)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    sox \
    espeak-ng \
    make \
    git \
    wget \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Stage 2: Python dependencies (separate layer for better caching)
FROM base AS python-deps

WORKDIR /app

# Copy and install Python requirements (cached if requirements.txt unchanged)
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 3: Final application image
FROM base AS final

WORKDIR /app

# Copy Python packages from previous stage
COPY --from=python-deps /root/.local /root/.local

# Copy application files
COPY src/ ./src/
COPY config.yaml .
COPY content/ ./content/
COPY .env.example .env
COPY Makefile .

# Create necessary directories
RUN mkdir -p output/{videos,shorts,thumbnails} credentials logs

# Make scripts executable
RUN chmod +x src/*.py

# Add local bin to PATH
ENV PATH=/root/.local/bin:$PATH

# Default command
CMD ["make", "help"]
