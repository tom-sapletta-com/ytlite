FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    sox \
    espeak-ng \
    make \
    git \
    wget \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create directories
RUN mkdir -p output/{videos,shorts,thumbnails} content/episodes credentials

# Set permissions
RUN chmod +x *.sh

CMD ["make", "help"]
