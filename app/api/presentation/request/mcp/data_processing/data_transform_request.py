from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

__all__ = [
    "DataTransformRequest",
]


class DataTransformRequest(BaseModel):
    """
    リクエストデータ（データ変換ツール）
    """

    data: str = Field(
        ...,
        description="変換対象のデータ（文字列形式）",
        max_length=1024 * 1024,  # 1MB制限
    )
    from_format: str = Field(
        ...,
        description="変換元フォーマット（json/csv/xml/yaml）",
        pattern=r"^(json|csv|xml|yaml)$",
    )
    to_format: str = Field(
        ...,
        description="変換先フォーマット（json/csv/xml/yaml）",
        pattern=r"^(json|csv|xml|yaml)$",
    )
    options: Optional[Dict[str, Any]] = Field(
        default=None,
        description="変換オプション",
    )
    field_mapping: Optional[Dict[str, str]] = Field(
        default=None,
        description="フィールド名マッピング（旧名: 新名）",
    )
    include_headers: bool = Field(
        default=True,
        description="CSVヘッダーを含めるか",
    )
    delimiter: str = Field(
        default=",",
        description="CSV区切り文字",
        max_length=1,
    )
    encoding: str = Field(
        default="utf-8",
        description="文字エンコーディング",
        pattern=r"^(utf-8|utf-16|shift_jis|euc-jp)$",
    )
