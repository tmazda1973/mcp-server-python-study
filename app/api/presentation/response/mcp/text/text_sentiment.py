from pydantic import BaseModel, Field

__all__ = [
    "TextSentiment",
]


class TextSentiment(BaseModel):
    """
    テキスト感情分析（簡易版）
    """

    polarity: float = Field(
        ...,
        description="極性スコア（-1: 負, 0: 中性, 1: 正）",
    )
    subjectivity: float = Field(
        ...,
        description="主観性スコア（0: 客観的, 1: 主観的）",
    )
    sentiment_label: str = Field(
        ...,
        description="感情ラベル（positive/negative/neutral）",
    )
    confidence: float = Field(
        ...,
        description="信頼度（0-1）",
    )
    emotional_keywords: list[str] = Field(
        ...,
        description="感情的なキーワード",
    )
