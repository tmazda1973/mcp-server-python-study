from pydantic import BaseModel, Field

__all__ = [
    "TextReplaceMatch",
]


class TextReplaceMatch(BaseModel):
    """
    テキスト置換マッチ情報
    """

    line_number: int = Field(..., description="行番号（1から開始）")
    original_line: str = Field(..., description="元の行内容")
    replaced_line: str = Field(..., description="置換後の行内容")
    match_start: int = Field(..., description="マッチ開始位置（行内での文字位置）")
    match_end: int = Field(..., description="マッチ終了位置（行内での文字位置）")
    original_text: str = Field(..., description="置換前のテキスト")
    replacement_text: str = Field(..., description="置換後のテキスト")
