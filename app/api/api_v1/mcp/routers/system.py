"""
システムツール用MCPルーター

- calculate: 数値計算
"""

from fastapi import APIRouter, Depends

from app.api.application.presenters import PresenterProtocol
from app.api.application.usecases.mcp import CalculateUsecase
from app.api.di.mcp import (
    provide_calculate_presenter,
    provide_calculate_usecase,
)
from app.api.presentation.request.mcp import CalculateRequest
from app.api.presentation.response.mcp import CalculateResponse

router = APIRouter()


@router.post(
    "/calculate",
    operation_id="calculate",
    description="2つの数値の計算（加算、減算、乗算、除算）を実行します。",
    summary="数値計算ツール",
)
async def calculate(
    request: CalculateRequest,
    presenter: PresenterProtocol[
        CalculateRequest,
        CalculateResponse,
    ] = Depends(provide_calculate_presenter),
    usecase: CalculateUsecase = Depends(provide_calculate_usecase),
) -> CalculateResponse:
    """
    数値計算（MCPツール）

    2つの数値を使用して基本的な計算を実行します：
    - 加算 (a + b)
    - 減算 (a - b)
    - 乗算 (a * b)
    - 除算 (a / b)

    Note:
        このエンドポイントは /mcp 経由でMCPツールとして利用可能です
    """
    presenter.request = request
    await usecase.execute(presenter)
    return presenter.response
