#!/bin/bash
set -e

GREEN="\033[0;32m"
YELLOW="\033[1;33m"
NC="\033[0m"

echo -e "${YELLOW}📝 Creating example WordPress test project...${NC}"

PROJECT="wordpress-test"
CONTENT_DIR="content/episodes"
PROJECT_DIR="output/projects/$PROJECT"

# Create content directory
mkdir -p "$CONTENT_DIR"

# Create example markdown content
cat > "$CONTENT_DIR/$PROJECT.md" << 'EOF'
---
title: "Test publikacji na WordPress"
date: 2025-01-15
theme: tech
template: gradient
voice: pl-PL-MarekNeural
tags: ["test", "wordpress", "ytlite"]
lang: pl
---

To jest przykładowy projekt do testowania publikacji na WordPress.

YTLite automatycznie generuje video z tego tekstu i publikuje na WordPress z miniaturką.

Funkcje testowane:
- Generowanie video z polskim głosem
- Tworzenie miniaturki
- Upload mediów do WordPress
- Publikacja artykułu z linkami do video

Ten projekt demonstruje pełny workflow od markdown do opublikowanego artykułu.
EOF

echo -e "${GREEN}✓ Created example content: $CONTENT_DIR/$PROJECT.md${NC}"

# Generate the project if not exists
if [ ! -f "$PROJECT_DIR/video.mp4" ]; then
    echo "Generating video project..."
    YTLITE_FAST_TEST=1 python3 src/ytlite_main.py generate "$CONTENT_DIR/$PROJECT.md"
fi

# Ensure .env exists
if [ ! -f "$PROJECT_DIR/.env" ]; then
    echo "Creating WordPress credentials..."
    cat > "$PROJECT_DIR/.env" << 'EOF'
# WordPress Test Environment Credentials
WORDPRESS_URL=http://localhost:8080
WORDPRESS_USERNAME=admin
WORDPRESS_APP_PASSWORD=admin123
UPLOAD_PRIVACY=public
PUBLIC_BASE_URL=http://localhost:5000
EOF
fi

echo -e "${GREEN}✓ Example project created: $PROJECT_DIR${NC}"
echo
echo "Project files:"
ls -la "$PROJECT_DIR/" 2>/dev/null || echo "Project directory not found - run generation first"
echo
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Start WordPress: bash scripts/setup-test-wordpress.sh"
echo "2. Start Web GUI: make gui" 
echo "3. Test publishing via Web GUI WordPress section"
echo "4. Or publish via CLI: python3 src/youtube_uploader.py upload-project --project $PROJECT"
