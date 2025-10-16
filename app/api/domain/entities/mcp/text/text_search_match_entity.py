from dataclasses import dataclass
from typing import List, Optional

__all__ = [
    "TextSearchMatchEntity",
]


@dataclass(frozen=True)
class TextSearchMatchEntity:
    """
    ドメインエンティティ（テキスト検索マッチ）
    """

    line_number: int
    line_content: str
    match_start: int
    match_end: int
    matched_text: str
    context_before: Optional[List[str]] = None
    context_after: Optional[List[str]] = None
