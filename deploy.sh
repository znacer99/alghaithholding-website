#!/bin/bash
set -e

APP_NAME="hrcopilot-app"
CONTAINER_NAME="hrcopilot-container"
PORT=5000

echo "Pulling latest code from GitHub..."
git reset --hard
git pull origin main

echo "Building Docker image..."
docker build -t "$APP_NAME" .

echo "Backing up database..."
cp instance/app.db instance/app.db.backup_$(date +%Y%m%d_%H%M%S)

echo "Stopping old container..."
docker stop "$CONTAINER_NAME" 2>/dev/null || true
docker rm "$CONTAINER_NAME" 2>/dev/null || true

echo "Starting new container..."
docker run -d \
  --name "$CONTAINER_NAME" \
  -p "$PORT:$PORT" \
  --env-file .env \
  -v "$(pwd)/uploads:/app/uploads" \
  -v "$(pwd)/instance:/app/instance" \
  -v "$(pwd)/static:/app/static" \
  "$APP_NAME"

echo "✅ Deployment complete! Database preserved."
