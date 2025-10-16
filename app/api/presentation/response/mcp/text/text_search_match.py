from typing import List, Optional

from pydantic import BaseModel, Field

__all__ = [
    "TextSearchMatch",
]


class TextSearchMatch(BaseModel):
    """
    テキスト検索マッチ情報
    """

    line_number: int = Field(..., description="行番号（1から開始）")
    line_content: str = Field(..., description="マッチした行の内容")
    match_start: int = Field(..., description="マッチ開始位置（行内での文字位置）")
    match_end: int = Field(..., description="マッチ終了位置（行内での文字位置）")
    matched_text: str = Field(..., description="マッチしたテキスト")
    context_before: Optional[List[str]] = Field(
        default=None,
        description="マッチした行より前のコンテキスト行",
    )
    context_after: Optional[List[str]] = Field(
        default=None,
        description="マッチした行より後のコンテキスト行",
    )
