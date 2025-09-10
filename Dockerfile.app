# YTLite App Image - Light application layer
FROM ytlite:base

LABEL description="YTLite application with code and content"

USER ytlite
WORKDIR /app

# Copy requirements and install Python dependencies
COPY --chown=ytlite:ytlite requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Copy application files
COPY --chown=ytlite:ytlite src/ ./src/
COPY --chown=ytlite:ytlite config.yaml .
COPY --chown=ytlite:ytlite content/ ./content/
COPY --chown=ytlite:ytlite .env.example .env
COPY --chown=ytlite:ytlite Makefile .

# Create necessary directories
RUN mkdir -p output/{videos,shorts,thumbnails} credentials logs

# Make scripts executable
RUN chmod +x src/*.py

# Add local bin to PATH
ENV PATH=/home/ytlite/.local/bin:$PATH

# Default command
CMD ["make", "help"]
