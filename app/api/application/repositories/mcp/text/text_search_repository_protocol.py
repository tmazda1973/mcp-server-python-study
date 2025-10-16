from typing import Protocol, runtime_checkable

from app.api.domain.entities.mcp.text import TextSearchResultEntity

__all__ = [
    "TextSearchRepositoryProtocol",
]


@runtime_checkable
class TextSearchRepositoryProtocol(Protocol):
    """
    リポジトリプロトコル（テキスト検索ツール）
    """

    async def search_text(
        self,
        text: str,
        pattern: str,
        case_sensitive: bool = False,
        use_regex: bool = False,
        whole_word: bool = False,
        max_matches: int = 0,
        include_line_numbers: bool = True,
        context_lines: int = 0,
    ) -> TextSearchResultEntity:
        """
        テキスト検索を実行する

        Args:
            text: 検索対象のテキスト
            pattern: 検索パターン（正規表現対応）
            case_sensitive: 大文字小文字を区別するか
            use_regex: 正規表現を使用するか
            whole_word: 単語全体マッチのみ
            max_matches: 最大マッチ数（0の場合は制限なし）
            include_line_numbers: 行番号を含めるか
            context_lines: マッチした行の前後の行数

        Returns:
            テキスト検索結果
        """
        ...
