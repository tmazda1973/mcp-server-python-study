import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi_mcp import FastApiMCP

from app.api.api_v1.router import router as api_v1_router
from app.core.config import settings
from app.core.error_handlers import register_error_handlers
from app.core.redis_util import close_redis, get_redis
from app.middlewares import IPRestrictionMiddleware

# ログ設定
logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL))
logger = logging.getLogger(__name__)

# uvicornのアクセスログロガーを取得
uvicorn_access_logger = logging.getLogger("uvicorn.access")


class HealthCheckFilter(logging.Filter):
    """
    ヘルスチェックエンドポイントのログを除外するフィルター
    """

    def filter(self, record: logging.LogRecord) -> bool:
        # /health エンドポイントのログを除外
        return "/health" not in record.getMessage()


# uvicornのアクセスログにフィルターを追加
uvicorn_access_logger.addFilter(HealthCheckFilter())


# ===== アプリケーションライフサイクル =====


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    アプリケーションのライフサイクル管理

    起動時と終了時の処理を定義します。
    """
    # 起動時の処理
    logger.info("FastAPI-MCP Server starting up...")

    # Redis接続テスト（将来的な拡張用、現在は未使用）
    # 接続できなくてもサーバーは正常に起動します
    redis_conn = await get_redis()
    if redis_conn:
        logger.info("✅ Redis connection established (for future use)")
    else:
        logger.info("ℹ️  Redis connection not configured or failed (not critical)")

    yield

    # 終了時の処理
    logger.info("🛑 FastAPI-MCP Server shutting down...")
    logger.info("⏳ Waiting for active requests to complete (timeout: 30s)...")

    # Redis接続を閉じる（接続されている場合のみ）
    await close_redis()
    logger.info("✅ Graceful shutdown completed")


# FastAPI アプリケーション初期化
app = FastAPI(
    title=settings.MCP_SERVER_NAME,
    description=settings.MCP_SERVER_DESCRIPTION,
    version="1.0.0",
    lifespan=lifespan,
)

# エラーハンドラを登録する
register_error_handlers(app)

# IP制限ミドルウェアを追加（AUTH_METHOD=ipの場合のみ有効）
if settings.AUTH_METHOD == "ip":
    logger.info(f"🔒 IP制限有効: {len(settings.ALLOWED_IPS)}個のIPアドレスを許可")
    logger.debug(f"許可IPリスト: {settings.ALLOWED_IPS}")
    app.add_middleware(IPRestrictionMiddleware)
else:
    logger.info(f"🔓 IP制限無効: AUTH_METHOD={settings.AUTH_METHOD}")

# CORS設定（必要に応じて）
if settings.ENABLE_CORS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS.split(",")
        if settings.CORS_ORIGINS
        else ["*"],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["*"],
    )

# APIルーターを追加
app.include_router(api_v1_router, prefix="/api/v1")


# ===== ルートレベルエンドポイント =====


@app.get("/", include_in_schema=False)
async def root():
    """
    ルートエンドポイント

    Swagger UI（API仕様書）にリダイレクトします。
    """
    return RedirectResponse(url="/docs")


@app.get("/health", operation_id="root_health_check")
async def health_check():
    """
    ヘルスチェックAPI
    """
    return {
        "status": "healthy",
        "server": settings.MCP_SERVER_NAME,
    }


@app.get("/info", operation_id="root_get_info")
async def get_info():
    """
    サーバー情報 取得API
    """
    return {
        "server_name": settings.MCP_SERVER_NAME,
        "version": "1.0.0",
        "environment": settings.APP_ENV,
        "host": settings.MCP_HOST,
        "port": str(settings.MCP_PORT),
    }


# ===== FastAPI-MCP設定 =====

# MCPツールとして公開するoperation_idを定義
MCP_TOOL_OPERATIONS = [
    # システムツール
    "calculate",
    # 外部APIツール
    "http_request",
    "rest_api_call",
    "webhook_send",
    # テキスト処理ツール
    "text_search",
    "text_replace",
    "text_analyze",
    # データ処理ツール
    "data_transform",
    "data_validate",
    "data_aggregate",
]

# IP制限による認証（AUTH_METHOD=ipで制御）
logger.info("🔓 MCP認証: IP制限ミドルウェアで制御（AUTH_METHOD設定を参照）")
mcp = FastApiMCP(
    app,
    name=settings.MCP_SERVER_NAME,
    description=settings.MCP_SERVER_DESCRIPTION,
    include_operations=MCP_TOOL_OPERATIONS,  # 特定のエンドポイントのみ公開
)

# MCPサーバーをマウント (複数プロトコル対応)
# SSE: /mcp
mcp.mount_sse(mount_path="/mcp")
# HTTP: /mcp-http
mcp.mount_http(mount_path="/mcp-http")
