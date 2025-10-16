from pydantic import BaseModel, Field

__all__ = [
    "TextSearchRequest",
]


class TextSearchRequest(BaseModel):
    """
    リクエストデータ（テキスト検索ツール）
    """

    text: str = Field(..., description="検索対象のテキスト")
    pattern: str = Field(..., description="検索パターン（正規表現対応）")
    case_sensitive: bool = Field(default=False, description="大文字小文字を区別するか")
    use_regex: bool = Field(default=False, description="正規表現を使用するか")
    whole_word: bool = Field(default=False, description="単語全体マッチのみ")
    max_matches: int = Field(
        default=0,
        ge=0,
        le=10000,
        description="最大マッチ数（0の場合は制限なし）",
    )
    include_line_numbers: bool = Field(default=True, description="行番号を含めるか")
    context_lines: int = Field(
        default=0,
        ge=0,
        le=10,
        description="マッチした行の前後の行数",
    )
