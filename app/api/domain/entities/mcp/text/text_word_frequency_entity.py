from dataclasses import dataclass
from typing import List

__all__ = [
    "WordFrequencyItemEntity",
    "TextWordFrequencyEntity",
]


@dataclass(frozen=True)
class WordFrequencyItemEntity:
    """
    ドメインエンティティ（単語頻度アイテム）
    """

    word: str
    count: int
    frequency: float


@dataclass(frozen=True)
class TextWordFrequencyEntity:
    """
    ドメインエンティティ（テキスト単語頻度分析）
    """

    total_unique_words: int
    most_common_words: List[WordFrequencyItemEntity]
    vocabulary_richness: float
