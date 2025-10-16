from dataclasses import dataclass

__all__ = [
    "TextReadabilityEntity",
]


@dataclass(frozen=True)
class TextReadabilityEntity:
    """
    ドメインエンティティ（テキスト読みやすさ指標）
    """

    flesch_reading_ease: float
    flesch_kincaid_grade: float
    automated_readability_index: float
    coleman_liau_index: float
    reading_level: str
    difficulty_assessment: str
