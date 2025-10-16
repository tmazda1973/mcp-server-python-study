from typing import Literal

from pydantic import BaseModel, Field

__all__ = [
    "CalculateRequest",
]


class CalculateRequest(BaseModel):
    """
    リクエストデータ（数値計算API）
    """

    a: float = Field(..., description="数値1")
    b: float = Field(..., description="数値2")
    operation: Literal["add", "subtract", "multiply", "divide"] = Field(
        default="add",
        description="演算子（add: 加算, subtract: 減算, multiply: 乗算, divide: 除算）",
    )
    api_key: str | None = None
