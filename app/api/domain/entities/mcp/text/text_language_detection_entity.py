from dataclasses import dataclass
from typing import List

__all__ = [
    "LanguageDetectionItemEntity",
    "TextLanguageDetectionEntity",
]


@dataclass(frozen=True)
class LanguageDetectionItemEntity:
    """
    ドメインエンティティ（言語検出アイテム）
    """

    language: str
    language_name: str
    confidence: float


@dataclass(frozen=True)
class TextLanguageDetectionEntity:
    """
    ドメインエンティティ（テキスト言語検出）
    """

    primary_language: LanguageDetectionItemEntity
    detected_languages: List[LanguageDetectionItemEntity]
    is_multilingual: bool
