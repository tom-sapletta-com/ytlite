#!/bin/bash

# Script to diagnose potential issues with Tauri app setup

echo "Diagnosing Tauri app setup issues..."

echo "1. Checking if required directories exist..."
if [ ! -d "/app/src-tauri/icons" ]; then
  echo "Error: Icons directory does not exist. Creating it..."
  mkdir -p /app/src-tauri/icons
fi
if [ ! -f "/app/src-tauri/icons/icon.png" ]; then
  echo "Error: Icon file does not exist. Creating a placeholder..."
  printf "\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\x0bIDAT\x08\xd7c\xf8\xff\xff\x3f\x00\x05\xfe\x02\xfe\xdc\xcc\x59\xe7\x00\x00\x00\x00IEND\xaeB\x60\x82" > /app/src-tauri/icons/icon.png
fi
if [ ! -d "/app/dist" ]; then
  echo "Error: Dist directory does not exist. Creating it..."
  mkdir -p /app/dist
fi

echo "2. Checking for port conflicts..."
if netstat -tuln | grep 1431 > /dev/null; then
  echo "Warning: Port 1431 is in use. Identifying process..."
  lsof -i :1431
fi

echo "3. Checking Tauri CLI version..."
npm list @tauri-apps/cli

echo "4. Checking Cargo.toml for Tauri dependencies..."
cat /app/src-tauri/Cargo.toml | grep tauri

echo "5. Checking if frontend build is needed..."
if [ -z "$(ls -A /app/dist)" ]; then
  echo "Warning: Dist directory is empty. Running frontend build..."
  cd /app && npm run build:frontend
fi

echo "6. Checking for permission issues..."
ls -ld /app /app/src-tauri /app/dist /app/src-tauri/icons

echo "Diagnosis complete. Check the output for any warnings or errors."
