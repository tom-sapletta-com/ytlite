#!/bin/bash

# Script to automate running Tauri app and Vite development server

echo "Starting Vite development server..."
cd /app && npm run vite-dev -- --port=1431 &
VITE_PID=$!

# Check if Vite server started successfully
echo "Checking if Vite server started on port 1431..."
sleep 5
if ! netstat -tuln | grep 1431 > /dev/null; then
  echo "Error: Vite server failed to start on port 1431. Checking for port conflicts..."
  lsof -i :1431
  echo "Attempting to kill process using port 1431..."
  kill -9 $(lsof -t -i :1431)
  echo "Retrying Vite server start..."
  cd /app && npm run vite-dev -- --port=1431 &
  VITE_PID=$!
  sleep 5
  if ! netstat -tuln | grep 1431 > /dev/null; then
    echo "Error: Vite server still failed to start. Trying a different port (1432)..."
    cd /app && npm run vite-dev -- --port=1432 &
    VITE_PID=$!
  fi
fi

echo "Starting Tauri app..."
cd /app/src-tauri && cargo run &
TAURI_PID=$!

echo "Tauri app and Vite server are running with PIDs $TAURI_PID and $VITE_PID"
echo "To stop the services, use: kill $TAURI_PID $VITE_PID"
