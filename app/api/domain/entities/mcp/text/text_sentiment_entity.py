from dataclasses import dataclass
from typing import List

__all__ = [
    "TextSentimentEntity",
]


@dataclass(frozen=True)
class TextSentimentEntity:
    """
    ドメインエンティティ（テキスト感情分析）
    """

    polarity: float
    subjectivity: float
    sentiment_label: str
    confidence: float
    emotional_keywords: List[str]
