#!/bin/bash
# Direct test script to verify environment

echo "=== Direct Environment Test ==="
echo "Current directory: $(pwd)"
echo "User: $(whoami)"
echo "Hostname: $(hostname)"
echo "Date: $(date)"
echo ""

echo "=== Python Environment ==="
which python3
python3 --version
python3 -c "import sys; print(f'Python path: {sys.executable}')"
echo ""

echo "=== File System Test ==="
touch test_file.txt
echo "Test content" > test_file.txt
cat test_file.txt
rm test_file.txt
echo ""

echo "=== Command Execution Test ==="
echo "Running 'ls -la'"
ls -la

echo ""
echo "=== Environment Variables ==="
echo "PATH: $PATH"
echo "HOME: $HOME"
echo "USER: $USER"

echo ""
echo "=== Process Information ==="
ps -ef | head -n 5

echo ""
echo "=== Test Complete ==="
