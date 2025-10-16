from dataclasses import dataclass
from typing import List, Optional

from .text_replace_match_entity import TextReplaceMatchEntity

__all__ = [
    "TextReplaceResultEntity",
]


@dataclass(frozen=True)
class TextReplaceResultEntity:
    """
    ドメインエンティティ（テキスト置換結果）
    """

    success: bool
    pattern: str
    replacement: str
    total_replacements: int
    total_lines: int
    modified_lines: int
    matches: List[TextReplaceMatchEntity]
    result_text: str
    truncated: bool
    preview_only: bool
    processing_time: float
    case_sensitive: bool
    use_regex: bool
    whole_word: bool
    error: Optional[str] = None
    warning: Optional[str] = None
