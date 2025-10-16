from typing import List, Optional

from pydantic import BaseModel, Field

from .text_search_match import TextSearchMatch

__all__ = [
    "TextSearchResponse",
]


class TextSearchResponse(BaseModel):
    """
    レスポンスデータ（テキスト検索ツール）
    """

    success: bool = Field(..., description="検索実行成功")
    pattern: str = Field(..., description="使用された検索パターン")
    total_matches: int = Field(..., description="総マッチ数")
    total_lines: int = Field(..., description="検索対象の総行数")
    matches: List[TextSearchMatch] = Field(..., description="マッチ結果一覧")
    truncated: bool = Field(..., description="結果が切り詰められたか")
    search_time: float = Field(..., description="検索実行時間（秒）")
    case_sensitive: bool = Field(..., description="大文字小文字区別設定")
    use_regex: bool = Field(..., description="正規表現使用設定")
    whole_word: bool = Field(..., description="単語全体マッチ設定")
    error: Optional[str] = Field(default=None, description="エラーメッセージ")
    warning: Optional[str] = Field(default=None, description="警告メッセージ")
