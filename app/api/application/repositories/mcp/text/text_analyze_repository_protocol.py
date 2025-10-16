from typing import List, Optional, Protocol, runtime_checkable

from app.api.domain.entities.mcp.text import TextAnalyzeResultEntity

__all__ = [
    "TextAnalyzeRepositoryProtocol",
]


@runtime_checkable
class TextAnalyzeRepositoryProtocol(Protocol):
    """
    リポジトリプロトコル（テキスト分析ツール）
    """

    async def analyze_text(
        self,
        text: str,
        include_basic_stats: bool = True,
        include_word_frequency: bool = True,
        include_readability: bool = True,
        include_sentiment: bool = False,
        include_language_detection: bool = True,
        word_frequency_limit: int = 20,
        min_word_length: int = 2,
        exclude_common_words: bool = True,
        custom_stop_words: Optional[List[str]] = None,
    ) -> TextAnalyzeResultEntity:
        """
        テキスト分析を実行する

        Args:
            text: 分析対象のテキスト
            include_basic_stats: 基本統計情報を含めるか
            include_word_frequency: 単語頻度分析を含めるか
            include_readability: 読みやすさ指標を含めるか
            include_sentiment: 感情分析を含めるか
            include_language_detection: 言語検出を含めるか
            word_frequency_limit: 単語頻度分析の上位表示数
            min_word_length: 単語頻度分析の最小単語長
            exclude_common_words: 一般的な単語を除外するか
            custom_stop_words: カスタムストップワードリスト

        Returns:
            テキスト分析結果
        """
        ...
