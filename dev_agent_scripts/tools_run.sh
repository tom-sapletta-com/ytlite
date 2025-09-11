#!/bin/bash
echo "[TOOLS] Running external CLI tools..."
for t in winsurf cursor; do
    if command -v $t &> /dev/null; then
        $t --run || echo "[TOOLS] $t failed"
    fi
done

