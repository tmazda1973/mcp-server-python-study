from typing import List, Optional

from pydantic import BaseModel, Field

__all__ = [
    "TextAnalyzeRequest",
]


class TextAnalyzeRequest(BaseModel):
    """
    リクエストデータ（テキスト分析ツール）
    """

    text: str = Field(..., description="分析対象のテキスト")
    include_basic_stats: bool = Field(
        default=True,
        description="基本統計情報を含めるか（文字数、行数、単語数など）",
    )
    include_word_frequency: bool = Field(
        default=True,
        description="単語頻度分析を含めるか",
    )
    include_readability: bool = Field(
        default=True,
        description="読みやすさ指標を含めるか",
    )
    include_sentiment: bool = Field(
        default=False,
        description="感情分析を含めるか（簡易版）",
    )
    include_language_detection: bool = Field(
        default=True,
        description="言語検出を含めるか",
    )
    word_frequency_limit: int = Field(
        default=20,
        ge=1,
        le=100,
        description="単語頻度分析の上位表示数",
    )
    min_word_length: int = Field(
        default=2,
        ge=1,
        le=10,
        description="単語頻度分析の最小単語長",
    )
    exclude_common_words: bool = Field(
        default=True,
        description="一般的な単語（ストップワード）を除外するか",
    )
    custom_stop_words: Optional[List[str]] = Field(
        default=None,
        description="カスタムストップワードリスト",
    )
