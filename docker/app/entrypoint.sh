#!/bin/bash

# conda環境をアクティベート
source activate fastapi-mcp

# .venv環境もアクティベート
source /usr/src/app/.venv/bin/activate

echo "🚀 Starting FastAPI-MCP Server..."

# Wait for database
if [ -n "${DATABASE_URL}" ]; then
    echo "⏳ Waiting for database..."
    while ! nc -z app-db 5432; do
        sleep 1
    done
    echo "✅ Database is ready!"
    
    # Run migrations
    echo "🔄 Running migrations..."
    echo "📍 Current directory: $(pwd)"
    echo "📍 Python path: $(which python)"
    echo "📍 Alembic path: $(which alembic)"
    alembic upgrade head
fi

# 環境変数で動作モードを切り替え（デフォルトはproduction）
APP_ENV=${APP_ENV:-production}

if [ "$APP_ENV" = "development" ]; then
    echo "🚀 Starting in DEVELOPMENT mode..."
    # FastAPI-MCPが安定動作するよう、一時的にリロード無効化
    # MCPサーバーはリロードで不安定になるため
    echo "⚠️  FastAPI-MCP安定動作のため、ホットリロードを一時的に無効化"
    exec uvicorn app.main:app \
        --host 0.0.0.0 \
        --port 8000 \
        --timeout-graceful-shutdown 30 \
        --timeout-keep-alive 5
else
    echo "🚀 Starting in PRODUCTION mode..."
    exec uvicorn app.main:app \
        --host 0.0.0.0 \
        --port 8000 \
        --workers 4 \
        --timeout-graceful-shutdown 30 \
        --timeout-keep-alive 5
fi
