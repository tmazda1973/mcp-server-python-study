from typing import Any, Dict, Optional, Protocol, runtime_checkable

from app.api.domain.entities.mcp.data_processing import DataTransformResultEntity

__all__ = [
    "DataTransformRepositoryProtocol",
]


@runtime_checkable
class DataTransformRepositoryProtocol(Protocol):
    """
    リポジトリプロトコル（データ変換ツール）
    """

    async def transform_data(
        self,
        data: str,
        from_format: str,
        to_format: str,
        options: Optional[Dict[str, Any]] = None,
        field_mapping: Optional[Dict[str, str]] = None,
        include_headers: bool = True,
        delimiter: str = ",",
        encoding: str = "utf-8",
    ) -> DataTransformResultEntity:
        """
        データ変換を実行する

        Args:
            data: 変換対象のデータ
            from_format: 変換元フォーマット
            to_format: 変換先フォーマット
            options: 変換オプション
            field_mapping: フィールド名マッピング
            include_headers: CSVヘッダーを含めるか
            delimiter: CSV区切り文字
            encoding: 文字エンコーディング

        Returns:
            データ変換結果
        """
        ...
