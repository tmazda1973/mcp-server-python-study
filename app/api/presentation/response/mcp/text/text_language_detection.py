from typing import List

from pydantic import BaseModel, Field

__all__ = [
    "LanguageDetectionItem",
    "TextLanguageDetection",
]


class LanguageDetectionItem(BaseModel):
    """
    言語検出アイテム
    """

    language: str = Field(..., description="言語コード（ISO 639-1）")
    language_name: str = Field(..., description="言語名")
    confidence: float = Field(..., description="信頼度（0-1）")


class TextLanguageDetection(BaseModel):
    """
    テキスト言語検出
    """

    primary_language: LanguageDetectionItem = Field(
        ...,
        description="主要言語",
    )
    detected_languages: List[LanguageDetectionItem] = Field(
        ...,
        description="検出された言語リスト（信頼度順）",
    )
    is_multilingual: bool = Field(
        ...,
        description="多言語テキストかどうか",
    )
