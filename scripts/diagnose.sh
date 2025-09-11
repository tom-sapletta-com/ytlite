#!/usr/bin/env bash
set -euo pipefail

# YTLite diagnostics: collects environment, versions, and smoke checks into JSON for LLMs
# Output: output/diagnostics/<timestamp>.json

ROOT_DIR=$(cd "$(dirname "$0")/.." && pwd)
OUT_DIR="$ROOT_DIR/output/diagnostics"
mkdir -p "$OUT_DIR"
TS=$(date -Iseconds)
OUT_FILE="$OUT_DIR/diagnostics-$TS.json"

json_escape() {
  python3 - <<'PY'
import json,sys
s=sys.stdin.read()
print(json.dumps(s))
PY
}

# Collect basics
PY_VER=$(python3 -c 'import sys; print(sys.version.replace("\n"," "))') || PY_VER="?"
FFMPEG_PATH=$(python3 - <<'PY'
try:
    import imageio_ffmpeg
    print(imageio_ffmpeg.get_ffmpeg_exe())
except Exception:
    print("")
PY
)
HAS_FFMPEG=0
if command -v ffmpeg >/dev/null 2>&1; then HAS_FFMPEG=1; fi
if [ -n "$FFMPEG_PATH" ]; then HAS_FFMPEG=1; fi

# Package versions (best-effort)
REQS=$(cat "$ROOT_DIR/requirements.txt" 2>/dev/null | sed 's/"/\"/g' | paste -sd"\\n" -)
PKG_VERS=$(python3 - <<'PY'
import pkgutil, pkg_resources, json
res={}
for dist in pkg_resources.working_set:
    res[dist.project_name]=dist.version
print(json.dumps(res))
PY
)

# Smoke: fast audio + 1 slide video (FAST_TEST)
export YTLITE_FAST_TEST=1
SMOKE_OK=1
SMOKE_LOG=""
MD_PATH="$ROOT_DIR/content/episodes/diag.md"
mkdir -p "$ROOT_DIR/content/episodes"
cat > "$MD_PATH" <<EOF
---
title: Diagnostics
---
Hello world
EOF
{
  set +e
  SMOKE_LOG=$(python3 -u "$ROOT_DIR/src/ytlite_main.py" generate "$MD_PATH" 2>&1)
  RC=$?
  if [ $RC -ne 0 ]; then SMOKE_OK=0; fi
  set -e
}

# Validate data
VALIDATE_DATA_JSON="$ROOT_DIR/output/validate_data.json"
VD_RC=0
{
  set +e
  bash "$ROOT_DIR/scripts/validate-data.sh" >/dev/null 2>&1
  VD_RC=$?
  set -e
}
VD_CONTENT=""
if [ -f "$VALIDATE_DATA_JSON" ]; then
  VD_CONTENT=$(cat "$VALIDATE_DATA_JSON")
fi

# Build JSON
cat > "$OUT_FILE" <<JSON
{
  "timestamp": "$TS",
  "python_version": "$(echo "$PY_VER" | sed 's/"/\"/g')",
  "has_ffmpeg": $HAS_FFMPEG,
  "imageio_ffmpeg": "$(echo "$FFMPEG_PATH" | sed 's/"/\"/g')",
  "env": {
    "IMAGEIO_FFMPEG_EXE": "${IMAGEIO_FFMPEG_EXE:-}",
    "LOG_LEVEL": "${LOG_LEVEL:-}",
    "YTLITE_FAST_TEST": "${YTLITE_FAST_TEST:-}",
    "PUBLIC_BASE_URL": "${PUBLIC_BASE_URL:-}",
    "SVG_ONLY": "${SVG_ONLY:-}"
  },
  "requirements": $(echo "$REQS" | json_escape),
  "packages": $PKG_VERS,
  "smoke": {
    "ok": $SMOKE_OK,
    "log": $(echo "$SMOKE_LOG" | json_escape)
  },
  "validate_data": {
    "rc": $VD_RC,
    "report": $(if [ -n "$VD_CONTENT" ]; then echo "$VD_CONTENT"; else echo "null"; fi)
  }
}
JSON

echo "Wrote diagnostics to $OUT_FILE"
