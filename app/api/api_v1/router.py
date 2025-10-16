from fastapi import APIRouter

from .mcp import router as mcp_router

router = APIRouter(tags=["api_v1"])

# サブルーターを追加する
router.include_router(mcp_router, prefix="/mcp")
