#!/bin/bash
echo "[TOOLS] Detecting external CLI tools..."
for t in windsurf cursor; do
    if command -v $t &> /dev/null; then
        echo "[TOOLS] Found $t"
    else
        echo "[TOOLS] $t not found, skipping"
    fi
done
