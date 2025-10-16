from typing import List

from typing_extensions import override

from app.api.application.presenters import PresenterProtocol
from app.api.application.repositories.mcp.text import TextAnalyzeRepositoryProtocol
from app.api.application.usecases.abstract_async_usecase import AbstractAsyncUsecase
from app.api.presentation.request.mcp.text import TextAnalyzeRequest
from app.api.presentation.response.mcp.text import (
    LanguageDetectionItem,
    TextAnalyzeResponse,
    TextBasicStats,
    TextLanguageDetection,
    TextReadability,
    TextSentiment,
    TextWordFrequency,
    WordFrequencyItem,
)

__all__ = [
    "TextAnalyzeUsecase",
]


class TextAnalyzeUsecase(
    AbstractAsyncUsecase[
        PresenterProtocol[
            TextAnalyzeRequest,
            TextAnalyzeResponse,
        ]
    ]
):
    """
    ユースケース（テキスト分析ツール）
    """

    def __init__(self, repository: TextAnalyzeRepositoryProtocol) -> None:
        self._repository = repository

    @override
    async def execute(
        self,
        presenter: PresenterProtocol[
            TextAnalyzeRequest,
            TextAnalyzeResponse,
        ],
    ) -> None:
        # テキスト分析を実行する
        request = presenter.request
        result = await self._repository.analyze_text(
            text=request.text,
            include_basic_stats=request.include_basic_stats,
            include_word_frequency=request.include_word_frequency,
            include_readability=request.include_readability,
            include_sentiment=request.include_sentiment,
            include_language_detection=request.include_language_detection,
            word_frequency_limit=request.word_frequency_limit,
            min_word_length=request.min_word_length,
            exclude_common_words=request.exclude_common_words,
            custom_stop_words=request.custom_stop_words,
        )

        # エンティティからレスポンスに変換
        basic_stats = None
        if result.basic_stats:
            basic_stats = TextBasicStats(
                total_characters=result.basic_stats.total_characters,
                total_characters_no_spaces=result.basic_stats.total_characters_no_spaces,
                total_lines=result.basic_stats.total_lines,
                total_paragraphs=result.basic_stats.total_paragraphs,
                total_words=result.basic_stats.total_words,
                total_sentences=result.basic_stats.total_sentences,
                average_words_per_sentence=result.basic_stats.average_words_per_sentence,
                average_characters_per_word=result.basic_stats.average_characters_per_word,
                longest_word=result.basic_stats.longest_word,
                longest_sentence_length=result.basic_stats.longest_sentence_length,
            )

        word_frequency = None
        if result.word_frequency:
            frequency_items: List[WordFrequencyItem] = []
            for item_entity in result.word_frequency.most_common_words:
                frequency_items.append(
                    WordFrequencyItem(
                        word=item_entity.word,
                        count=item_entity.count,
                        frequency=item_entity.frequency,
                    )
                )

            word_frequency = TextWordFrequency(
                total_unique_words=result.word_frequency.total_unique_words,
                most_common_words=frequency_items,
                vocabulary_richness=result.word_frequency.vocabulary_richness,
            )

        readability = None
        if result.readability:
            readability = TextReadability(
                flesch_reading_ease=result.readability.flesch_reading_ease,
                flesch_kincaid_grade=result.readability.flesch_kincaid_grade,
                automated_readability_index=result.readability.automated_readability_index,
                coleman_liau_index=result.readability.coleman_liau_index,
                reading_level=result.readability.reading_level,
                difficulty_assessment=result.readability.difficulty_assessment,
            )

        sentiment = None
        if result.sentiment:
            sentiment = TextSentiment(
                polarity=result.sentiment.polarity,
                subjectivity=result.sentiment.subjectivity,
                sentiment_label=result.sentiment.sentiment_label,
                confidence=result.sentiment.confidence,
                emotional_keywords=result.sentiment.emotional_keywords,
            )

        language_detection = None
        if result.language_detection:
            detected_items: List[LanguageDetectionItem] = []
            for lang_entity in result.language_detection.detected_languages:
                detected_items.append(
                    LanguageDetectionItem(
                        language=lang_entity.language,
                        language_name=lang_entity.language_name,
                        confidence=lang_entity.confidence,
                    )
                )

            primary_language = LanguageDetectionItem(
                language=result.language_detection.primary_language.language,
                language_name=result.language_detection.primary_language.language_name,
                confidence=result.language_detection.primary_language.confidence,
            )

            language_detection = TextLanguageDetection(
                primary_language=primary_language,
                detected_languages=detected_items,
                is_multilingual=result.language_detection.is_multilingual,
            )

        presenter.response = TextAnalyzeResponse(
            success=result.success,
            text_length=result.text_length,
            analysis_time=result.analysis_time,
            basic_stats=basic_stats,
            word_frequency=word_frequency,
            readability=readability,
            sentiment=sentiment,
            language_detection=language_detection,
            error=result.error,
            warning=result.warning,
        )
