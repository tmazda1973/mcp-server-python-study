from typing import List

from pydantic import BaseModel, Field

__all__ = [
    "WordFrequencyItem",
    "TextWordFrequency",
]


class WordFrequencyItem(BaseModel):
    """
    単語頻度アイテム
    """

    word: str = Field(..., description="単語")
    count: int = Field(..., description="出現回数")
    frequency: float = Field(..., description="出現頻度（0-1）")


class TextWordFrequency(BaseModel):
    """
    テキスト単語頻度分析
    """

    total_unique_words: int = Field(
        ...,
        description="ユニーク単語数",
    )
    most_common_words: List[WordFrequencyItem] = Field(
        ...,
        description="頻出単語リスト",
    )
    vocabulary_richness: float = Field(
        ...,
        description="語彙の豊富さ（ユニーク単語数/総単語数）",
    )
