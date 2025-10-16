"""
MCP統合ルーター

各ツール種別のサブルーターを統合し、
MCPプロトコルでアクセス可能なエンドポイントを提供します。
"""

from fastapi import APIRouter

from app.api.api_v1.mcp.routers.data_processing import router as data_processing_router
from app.api.api_v1.mcp.routers.external_api import router as external_api_router
from app.api.api_v1.mcp.routers.system import router as system_router
from app.api.api_v1.mcp.routers.text import router as text_router

router = APIRouter()

# システムツール
router.include_router(
    system_router,
    prefix="/system",
    tags=["システムツール"],
)

# 外部APIツール
router.include_router(
    external_api_router,
    prefix="/external-api",
    tags=["外部APIツール"],
)

# テキスト処理ツール
router.include_router(
    text_router,
    prefix="/text",
    tags=["テキスト処理ツール"],
)

# データ処理ツール
router.include_router(
    data_processing_router,
    prefix="/data",
    tags=["データ処理ツール"],
)
