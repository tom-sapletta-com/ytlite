#!/bin/bash
set -e

GREEN="\033[0;32m"
YELLOW="\033[1;33m"
RED="\033[0;31m"
NC="\033[0m"

echo -e "${YELLOW}🩺 Validating application (deps + smoke generate + packaging)...${NC}"

# 1) Dependencies
python3 -u src/ytlite_main.py check

# 2) Pick or create a sample markdown
SAMPLE_MD=$(ls content/episodes/*.md 2>/dev/null | head -n1)
if [ -z "$SAMPLE_MD" ]; then
  mkdir -p content/episodes
  SAMPLE_MD="content/episodes/sample_validate.md"
  cat > "$SAMPLE_MD" << 'EOF'
---
title: "Validation Sample"
date: 2025-01-01
theme: tech
---

To jest przykładowy tekst do walidacji aplikacji.
EOF
fi

BASENAME=$(basename "$SAMPLE_MD" .md)

# 3) Generate
python3 -u src/ytlite_main.py generate "$SAMPLE_MD"

# 4) Check project packaging
PROJECT_DIR="output/projects/$BASENAME"
REQUIRED=(video.mp4 audio.mp3 thumbnail.jpg description.md index.md)
MISSING=()
for f in "${REQUIRED[@]}"; do
  if [ ! -f "$PROJECT_DIR/$f" ]; then
    MISSING+=("$f")
  fi
done

TIMESTAMP=$(date -Iseconds)
REPORT_JSON="$PROJECT_DIR/app_validate.json"
REPORT_MD="$PROJECT_DIR/app_validate.md"

# Prepare JSON
STATUS="ok"
if [ ${#MISSING[@]} -gt 0 ]; then STATUS="failed"; fi

mkdir -p "$PROJECT_DIR"
cat > "$REPORT_JSON" <<JSON
{
  "timestamp": "$TIMESTAMP",
  "sample": "$SAMPLE_MD",
  "project": "$PROJECT_DIR",
  "required": ["video.mp4", "audio.mp3", "thumbnail.jpg", "description.md", "index.md"],
  "missing": ["${MISSING[@]}"] ,
  "status": "$STATUS"
}
JSON

# Prepare Markdown
{
  echo "# App Validation Report"
  echo ""
  echo "- Timestamp: $TIMESTAMP"
  echo "- Sample: $SAMPLE_MD"
  echo "- Project: $PROJECT_DIR"
  echo ""
  echo "## Required Files"
  for f in "${REQUIRED[@]}"; do
    if [ -f "$PROJECT_DIR/$f" ]; then
      echo "- $f: ✓"
    else
      echo "- $f: ✗"
    fi
  done
  if [ ${#MISSING[@]} -gt 0 ]; then
    echo ""
    echo "## Missing"
    for m in "${MISSING[@]}"; do echo "- $m"; done
  fi
} > "$REPORT_MD"

if [ ${#MISSING[@]} -gt 0 ]; then
  echo -e "${RED} Packaging missing files in $PROJECT_DIR: ${MISSING[*]}${NC}"
  exit 1
fi

echo -e "${GREEN} Application validation passed${NC}"
