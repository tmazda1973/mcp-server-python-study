from dataclasses import dataclass
from typing import List, Optional

from .text_search_match_entity import TextSearchMatchEntity

__all__ = [
    "TextSearchResultEntity",
]


@dataclass(frozen=True)
class TextSearchResultEntity:
    """
    ドメインエンティティ（テキスト検索結果）
    """

    success: bool
    pattern: str
    total_matches: int
    total_lines: int
    matches: List[TextSearchMatchEntity]
    truncated: bool
    search_time: float
    case_sensitive: bool
    use_regex: bool
    whole_word: bool
    error: Optional[str] = None
    warning: Optional[str] = None
