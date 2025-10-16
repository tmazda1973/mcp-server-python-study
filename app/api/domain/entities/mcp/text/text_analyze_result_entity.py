from dataclasses import dataclass
from typing import Optional

from .text_basic_stats_entity import TextBasicStatsEntity
from .text_language_detection_entity import TextLanguageDetectionEntity
from .text_readability_entity import TextReadabilityEntity
from .text_sentiment_entity import TextSentimentEntity
from .text_word_frequency_entity import TextWordFrequencyEntity

__all__ = [
    "TextAnalyzeResultEntity",
]


@dataclass(frozen=True)
class TextAnalyzeResultEntity:
    """
    ドメインエンティティ（テキスト分析結果）
    """

    success: bool
    text_length: int
    analysis_time: float
    basic_stats: Optional[TextBasicStatsEntity] = None
    word_frequency: Optional[TextWordFrequencyEntity] = None
    readability: Optional[TextReadabilityEntity] = None
    sentiment: Optional[TextSentimentEntity] = None
    language_detection: Optional[TextLanguageDetectionEntity] = None
    error: Optional[str] = None
    warning: Optional[str] = None
