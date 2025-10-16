from pydantic import BaseModel, Field

__all__ = [
    "TextReadability",
]


class TextReadability(BaseModel):
    """
    テキスト読みやすさ指標
    """

    flesch_reading_ease: float = Field(
        ...,
        description="Flesch Reading Ease スコア",
    )
    flesch_kincaid_grade: float = Field(
        ...,
        description="Flesch-Kincaid Grade Level",
    )
    automated_readability_index: float = Field(
        ...,
        description="Automated Readability Index",
    )
    coleman_liau_index: float = Field(
        ...,
        description="Coleman-Liau Index",
    )
    reading_level: str = Field(
        ...,
        description="読書レベル（簡易判定）",
    )
    difficulty_assessment: str = Field(
        ...,
        description="難易度評価",
    )
