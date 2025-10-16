"""
データ処理ツール用MCPルーター

- data_transform: データ変換（JSON、CSV、XML、YAML）
- data_validate: データ検証（JSON Schema、カスタムルール）
- data_aggregate: データ集計（グループ化、集計関数、フィルタリング）
"""

from fastapi import APIRouter, Depends

from app.api.application.presenters import PresenterProtocol
from app.api.application.usecases.mcp.data_processing import (
    DataAggregateUsecase,
    DataTransformUsecase,
    DataValidateUsecase,
)
from app.api.di.mcp.data_processing import (
    provide_data_aggregate_presenter,
    provide_data_aggregate_usecase,
    provide_data_transform_presenter,
    provide_data_transform_usecase,
    provide_data_validate_presenter,
    provide_data_validate_usecase,
)
from app.api.presentation.request.mcp.data_processing import (
    DataAggregateRequest,
    DataTransformRequest,
    DataValidateRequest,
)
from app.api.presentation.response.mcp.data_processing import (
    DataAggregateResponse,
    DataTransformResponse,
    DataValidateResponse,
)

router = APIRouter()


@router.post(
    "/transform",
    operation_id="data_transform",
    description="JSON、CSV、XML、YAML形式間でのデータ変換を行います。フィールドマッピングや文字エンコーディング変換にも対応。",
    summary="データ変換ツール",
)
async def data_transform(
    request: DataTransformRequest,
    presenter: PresenterProtocol[
        DataTransformRequest,
        DataTransformResponse,
    ] = Depends(provide_data_transform_presenter),
    usecase: DataTransformUsecase = Depends(provide_data_transform_usecase),
) -> DataTransformResponse:
    """
    データ変換（MCPツール）

    異なるデータ形式間での変換を実行します：
    - JSON ↔ CSV ↔ XML ↔ YAML 変換
    - フィールド名マッピング機能
    - 文字エンコーディング変換
    - CSV区切り文字カスタマイズ

    Note:
        このエンドポイントは /mcp 経由でMCPツールとして利用可能です
    """
    presenter.request = request
    await usecase.execute(presenter)
    return presenter.response


@router.post(
    "/validate",
    operation_id="data_validate",
    description="JSON Schema、カスタムルールによるデータ検証を実行します。厳密・寛容・報告専用の3つのモードに対応。",
    summary="データ検証ツール",
)
async def data_validate(
    request: DataValidateRequest,
    presenter: PresenterProtocol[
        DataValidateRequest,
        DataValidateResponse,
    ] = Depends(provide_data_validate_presenter),
    usecase: DataValidateUsecase = Depends(provide_data_validate_usecase),
) -> DataValidateResponse:
    """
    データ検証（MCPツール）

    データの検証とスキーマチェックを実行します：
    - JSON Schema検証
    - カスタムルール検証
    - 検証モード（strict/lenient/report_only）
    - エラー・警告レポート
    - 改善推奨事項

    Note:
        このエンドポイントは /mcp 経由でMCPツールとして利用可能です
    """
    presenter.request = request
    await usecase.execute(presenter)
    return presenter.response


@router.post(
    "/aggregate",
    operation_id="data_aggregate",
    description="JSON配列データのグループ化・集計処理を実行します。複数の集計関数、フィルタリング、ソートに対応。",
    summary="データ集計ツール",
)
async def data_aggregate(
    request: DataAggregateRequest,
    presenter: PresenterProtocol[
        DataAggregateRequest,
        DataAggregateResponse,
    ] = Depends(provide_data_aggregate_presenter),
    usecase: DataAggregateUsecase = Depends(provide_data_aggregate_usecase),
) -> DataAggregateResponse:
    """
    データ集計（MCPツール）

    データの集計と統計処理を実行します：
    - グループ化（複数フィールド対応）
    - 集計関数（count, sum, avg, min, max, distinct等）
    - フィルタリング（複雑な条件対応）
    - ソート（複数フィールド・昇順降順）
    - 統計情報・メタデータ生成

    Note:
        このエンドポイントは /mcp 経由でMCPツールとして利用可能です
    """
    presenter.request = request
    await usecase.execute(presenter)
    return presenter.response
