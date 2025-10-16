from typing import Protocol, runtime_checkable

from app.api.domain.entities.mcp.text import TextReplaceResultEntity

__all__ = [
    "TextReplaceRepositoryProtocol",
]


@runtime_checkable
class TextReplaceRepositoryProtocol(Protocol):
    """
    リポジトリプロトコル（テキスト置換ツール）
    """

    async def replace_text(
        self,
        text: str,
        pattern: str,
        replacement: str,
        case_sensitive: bool = False,
        use_regex: bool = False,
        whole_word: bool = False,
        max_replacements: int = 0,
        preview_only: bool = False,
    ) -> TextReplaceResultEntity:
        """
        テキスト置換を実行する

        Args:
            text: 置換対象のテキスト
            pattern: 検索パターン（正規表現対応）
            replacement: 置換文字列
            case_sensitive: 大文字小文字を区別するか
            use_regex: 正規表現を使用するか
            whole_word: 単語全体マッチのみ
            max_replacements: 最大置換数（0の場合は制限なし）
            preview_only: プレビューのみ（実際の置換は行わない）

        Returns:
            テキスト置換結果
        """
        ...
