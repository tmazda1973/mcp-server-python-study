from pydantic import BaseModel, Field

__all__ = [
    "TextReplaceRequest",
]


class TextReplaceRequest(BaseModel):
    """
    リクエストデータ（テキスト置換ツール）
    """

    text: str = Field(..., description="置換対象のテキスト")
    pattern: str = Field(..., description="検索パターン（正規表現対応）")
    replacement: str = Field(..., description="置換文字列")
    case_sensitive: bool = Field(default=False, description="大文字小文字を区別するか")
    use_regex: bool = Field(default=False, description="正規表現を使用するか")
    whole_word: bool = Field(default=False, description="単語全体マッチのみ")
    max_replacements: int = Field(
        default=0,
        ge=0,
        le=10000,
        description="最大置換数（0の場合は制限なし）",
    )
    preview_only: bool = Field(
        default=False,
        description="プレビューのみ（実際の置換は行わない）",
    )
