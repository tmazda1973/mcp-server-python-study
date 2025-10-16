from dataclasses import dataclass

__all__ = [
    "TextReplaceMatchEntity",
]


@dataclass(frozen=True)
class TextReplaceMatchEntity:
    """
    ドメインエンティティ（テキスト置換マッチ）
    """

    line_number: int
    original_line: str
    replaced_line: str
    match_start: int
    match_end: int
    original_text: str
    replacement_text: str
