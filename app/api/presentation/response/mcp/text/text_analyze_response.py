from typing import Optional

from pydantic import BaseModel, Field

from .text_basic_stats import TextBasicStats
from .text_language_detection import TextLanguageDetection
from .text_readability import TextReadability
from .text_sentiment import TextSentiment
from .text_word_frequency import TextWordFrequency

__all__ = [
    "TextAnalyzeResponse",
]


class TextAnalyzeResponse(BaseModel):
    """
    レスポンスデータ（テキスト分析ツール）
    """

    success: bool = Field(..., description="分析実行成功")
    text_length: int = Field(..., description="分析対象テキストの文字数")
    analysis_time: float = Field(..., description="分析実行時間（秒）")
    basic_stats: Optional[TextBasicStats] = Field(
        default=None,
        description="基本統計情報",
    )
    word_frequency: Optional[TextWordFrequency] = Field(
        default=None,
        description="単語頻度分析",
    )
    readability: Optional[TextReadability] = Field(
        default=None,
        description="読みやすさ指標",
    )
    sentiment: Optional[TextSentiment] = Field(
        default=None,
        description="感情分析",
    )
    language_detection: Optional[TextLanguageDetection] = Field(
        default=None,
        description="言語検出",
    )
    error: Optional[str] = Field(
        default=None,
        description="エラーメッセージ",
    )
    warning: Optional[str] = Field(
        default=None,
        description="警告メッセージ",
    )
