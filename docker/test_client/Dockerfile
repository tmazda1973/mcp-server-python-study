# テスト用クライアントコンテナ
FROM python:3.11-slim

# メタデータ
LABEL maintainer="FastAPI-MCP Team" \
      description="FastAPI-MCP テストクライアント" \
      version="1.0.0"

WORKDIR /app

# システムパッケージの更新とクリーンアップ
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl \
        netcat-openbsd \
        make && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 必要なPythonパッケージをインストール
RUN pip install --no-cache-dir \
    httpx \
    typer[all] \
    rich

# tty: true で待機するため、デフォルトコマンドは不要
CMD ["sleep", "infinity"]
