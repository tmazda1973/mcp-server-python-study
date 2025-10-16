from typing import Any

from pydantic import BaseModel

__all__ = [
    "CalculateResponse",
]


class CalculateResponse(BaseModel):
    """
    レスポンスデータ（数値計算API）
    """

    operation: str
    inputs: dict[str, Any]
    result: float
    mcp_tool: bool
