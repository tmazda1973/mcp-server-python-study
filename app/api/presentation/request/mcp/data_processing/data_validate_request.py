from typing import Any

from pydantic import BaseModel, Field

__all__ = [
    "DataValidateRequest",
]


class DataValidateRequest(BaseModel):
    """
    リクエストデータ（データ検証ツール）
    """

    data: str = Field(
        ...,
        max_length=1_048_576,  # 1MB制限
        description="検証対象のデータ（JSON文字列形式）",
    )

    schema_type: str = Field(
        ...,
        pattern=r"^(json_schema|pydantic|custom)$",
        description="スキーマタイプ（json_schema/pydantic/custom）",
    )

    schema_definition: str = Field(
        ...,
        max_length=102_400,  # 100KB制限
        description="スキーマ定義（JSON Schema、Pydanticモデル、またはカスタムルール）",
    )

    validation_mode: str = Field(
        default="strict",
        pattern=r"^(strict|lenient|report_only)$",
        description="検証モード（strict: 厳密/lenient: 寛容/report_only: 報告のみ）",
    )

    max_errors: int = Field(
        default=50,
        ge=1,
        le=500,
        description="報告する最大エラー数",
    )

    include_warnings: bool = Field(
        default=True,
        description="警告も含めるか",
    )

    custom_rules: dict[str, Any] | None = Field(
        default=None,
        description="カスタム検証ルール",
    )

    api_key: str | None = Field(default=None, description="API Key")
