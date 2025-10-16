"""
FastAPI-MCP Server Entry Point
"""

import os

import uvicorn

if __name__ == "__main__":
    # 環境変数から設定取得
    host = os.environ.get("MCP_HOST", "127.0.0.1")
    port = int(os.environ.get("MCP_PORT", "8000"))
    log_level = os.environ.get("LOG_LEVEL", "info").lower()

    print(f"🚀 Starting FastAPI-MCP Server on {host}:{port}")
    print(f"📄 API Documentation: http://{host}:{port}/docs")
    print(f"🔗 MCP Endpoint: http://{host}:{port}/mcp")

    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        log_level=log_level,
        reload=os.environ.get("APP_ENV") == "development",
        timeout_graceful_shutdown=30,  # グレースフルシャットダウンのタイムアウト（秒）
        timeout_keep_alive=5,  # Keep-Aliveタイムアウト（秒）
    )
