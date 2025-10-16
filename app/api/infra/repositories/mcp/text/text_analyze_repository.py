import re
import time
from collections import Counter
from typing import List, Optional

from typing_extensions import override

from app.api.application.repositories.mcp.text import TextAnalyzeRepositoryProtocol
from app.api.domain.entities.mcp.text import (
    LanguageDetectionItemEntity,
    TextAnalyzeResultEntity,
    TextBasicStatsEntity,
    TextLanguageDetectionEntity,
    TextReadabilityEntity,
    TextSentimentEntity,
    TextWordFrequencyEntity,
    WordFrequencyItemEntity,
)
from app.decorators.access_control import private

__all__ = [
    "TextAnalyzeRepository",
]


class TextAnalyzeRepository(TextAnalyzeRepositoryProtocol):
    """
    リポジトリ（テキスト分析ツール）
    """

    def __init__(self) -> None:
        # 基本的なストップワード（日本語・英語）
        self._default_stop_words = {
            # 英語
            "a",
            "an",
            "and",
            "are",
            "as",
            "at",
            "be",
            "by",
            "for",
            "from",
            "has",
            "he",
            "in",
            "is",
            "it",
            "its",
            "of",
            "on",
            "that",
            "the",
            "to",
            "was",
            "will",
            "with",
            "would",
            "you",
            "your",
            "have",
            "had",
            "this",
            "these",
            "they",
            "them",
            "their",
            "there",
            "where",
            "when",
            "what",
            "who",
            "how",
            "can",
            "could",
            "should",
            "may",
            "might",
            "must",
            "shall",
            "do",
            "does",
            "did",
            "not",
            "no",
            "yes",
            "but",
            "or",
            "so",
            "if",
            "then",
            "than",
            "more",
            "most",
            "some",
            "any",
            "all",
            "each",
            "every",
            "both",
            "either",
            "neither",
            "one",
            "two",
            "first",
            "last",
            "only",
            "just",
            "very",
            "too",
            "much",
            "many",
            "few",
            "little",
            "big",
            "small",
            "good",
            "bad",
            "new",
            "old",
            # 日本語
            "が",
            "の",
            "を",
            "に",
            "へ",
            "と",
            "で",
            "は",
            "も",
            "から",
            "まで",
            "より",
            "という",
            "として",
            "について",
            "において",
            "による",
            "によって",
            "です",
            "である",
            "だ",
            "ある",
            "いる",
            "する",
            "した",
            "される",
            "された",
            "れる",
            "られる",
            "せる",
            "させる",
            "ない",
            "なかった",
            "この",
            "その",
            "あの",
            "どの",
            "これ",
            "それ",
            "あれ",
            "どれ",
            "ここ",
            "そこ",
            "あそこ",
            "どこ",
            "こう",
            "そう",
            "ああ",
            "どう",
            "など",
            "なども",
            "または",
            "及び",
            "および",
            "かつ",
            "しかし",
            "ただし",
            "また",
            "さらに",
            "そして",
            "それで",
            "それから",
            "そこで",
        }

        # 感情分析用キーワード（簡易版）
        self._positive_words = {
            "good",
            "great",
            "excellent",
            "amazing",
            "wonderful",
            "fantastic",
            "awesome",
            "perfect",
            "beautiful",
            "love",
            "like",
            "happy",
            "joy",
            "pleased",
            "satisfied",
            "delighted",
            "thrilled",
            "excited",
            "良い",
            "素晴らしい",
            "素晴",  # 分割された形
            "らしい",  # 分割された形
            "最高",
            "すごい",
            "いい",
            "好き",
            "嬉しい",
            "嬉",  # 分割された形
            "しい",  # 分割された形（ポジティブ）
            "楽しい",
            "楽",  # 分割された形
            "しみ",  # 分割された形
            "満足",
            "喜び",
            "喜",  # 分割された形
            "感動",
            "感謝",
            "ありがとう",
            "幸せ",
            "幸",  # 分割された形
            "便利",
            "便",  # 分割された形
            "利",  # 分割された形
        }

        self._negative_words = {
            "bad",
            "terrible",
            "awful",
            "horrible",
            "disgusting",
            "hate",
            "dislike",
            "sad",
            "angry",
            "frustrated",
            "disappointed",
            "upset",
            "annoyed",
            "worried",
            "concerned",
            "problem",
            "issue",
            "error",
            "悪い",
            "ひどい",
            "最悪",
            "嫌い",
            "嫌",
            "悲しい",
            "怒り",
            "腹立つ",
            "困る",
            "心配",
            "不安",
            "問題",
            "エラー",
            "失敗",
            "だめ",
            "いけない",
        }

        # 言語検出用パターン（簡易版）
        self._language_patterns = {
            "ja": re.compile(r"[ぁ-んァ-ヶー]"),
            "en": re.compile(r"[a-zA-Z]"),
            "zh": re.compile(r"[一-龯]"),
            "ko": re.compile(r"[가-힣]"),
            "ar": re.compile(r"[ء-ي]"),
            "ru": re.compile(r"[а-яё]", re.IGNORECASE),
        }

        self._language_names = {
            "ja": "Japanese",
            "en": "English",
            "zh": "Chinese",
            "ko": "Korean",
            "ar": "Arabic",
            "ru": "Russian",
        }

    @override
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
        start_time = time.time()

        try:
            # 基本統計情報
            basic_stats = None
            if include_basic_stats:
                basic_stats = await self._analyze_basic_stats(text)

            # 単語頻度分析
            word_frequency = None
            if include_word_frequency:
                word_frequency = await self._analyze_word_frequency(
                    text,
                    word_frequency_limit,
                    min_word_length,
                    exclude_common_words,
                    custom_stop_words,
                )

            # 読みやすさ指標
            readability = None
            if include_readability:
                readability = await self._analyze_readability(text)

            # 感情分析
            sentiment = None
            if include_sentiment:
                sentiment = await self._analyze_sentiment(text)

            # 言語検出
            language_detection = None
            if include_language_detection:
                language_detection = await self._detect_language(text)

            analysis_time = time.time() - start_time

            return TextAnalyzeResultEntity(
                success=True,
                text_length=len(text),
                analysis_time=analysis_time,
                basic_stats=basic_stats,
                word_frequency=word_frequency,
                readability=readability,
                sentiment=sentiment,
                language_detection=language_detection,
            )

        except Exception as e:
            analysis_time = time.time() - start_time
            return TextAnalyzeResultEntity(
                success=False,
                text_length=len(text),
                analysis_time=analysis_time,
                error=f"分析エラー: {str(e)}",
            )

    @private
    async def _analyze_basic_stats(self, text: str) -> TextBasicStatsEntity:
        """基本統計情報を分析する"""
        lines = text.splitlines()
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

        # 単語分割（英語・日本語対応）
        words = self._extract_words(text)

        # 文分割
        sentences = self._extract_sentences(text)

        # 統計計算
        total_characters = len(text)
        total_characters_no_spaces = len(
            text.replace(" ", "").replace("\t", "").replace("\n", "")
        )
        total_lines = len(lines)
        total_paragraphs = len(paragraphs)
        total_words = len(words)
        total_sentences = len(sentences)

        avg_words_per_sentence = total_words / max(total_sentences, 1)
        avg_chars_per_word = sum(len(word) for word in words) / max(total_words, 1)

        longest_word = max(words, key=len) if words else ""
        longest_sentence_length = max(len(s) for s in sentences) if sentences else 0

        return TextBasicStatsEntity(
            total_characters=total_characters,
            total_characters_no_spaces=total_characters_no_spaces,
            total_lines=total_lines,
            total_paragraphs=total_paragraphs,
            total_words=total_words,
            total_sentences=total_sentences,
            average_words_per_sentence=avg_words_per_sentence,
            average_characters_per_word=avg_chars_per_word,
            longest_word=longest_word,
            longest_sentence_length=longest_sentence_length,
        )

    @private
    async def _analyze_word_frequency(
        self,
        text: str,
        limit: int,
        min_length: int,
        exclude_common: bool,
        custom_stop_words: Optional[List[str]],
    ) -> TextWordFrequencyEntity:
        """単語頻度分析を実行する"""
        words = self._extract_words(text.lower())

        # フィルタリング
        filtered_words = []
        stop_words = set()

        if exclude_common:
            stop_words.update(self._default_stop_words)

        if custom_stop_words:
            stop_words.update(word.lower() for word in custom_stop_words)

        for word in words:
            if len(word) >= min_length and word not in stop_words:
                filtered_words.append(word)

        # 頻度計算
        word_counts = Counter(filtered_words)
        total_words = len(filtered_words)
        unique_words = len(word_counts)

        # 上位単語
        most_common = word_counts.most_common(limit)
        frequency_items = [
            WordFrequencyItemEntity(
                word=word,
                count=count,
                frequency=count / max(total_words, 1),
            )
            for word, count in most_common
        ]

        # 語彙の豊富さ
        vocabulary_richness = unique_words / max(total_words, 1)

        return TextWordFrequencyEntity(
            total_unique_words=unique_words,
            most_common_words=frequency_items,
            vocabulary_richness=vocabulary_richness,
        )

    @private
    async def _analyze_readability(self, text: str) -> TextReadabilityEntity:
        """読みやすさ指標を分析する"""
        words = self._extract_words(text)
        sentences = self._extract_sentences(text)

        if not words or not sentences:
            return TextReadabilityEntity(
                flesch_reading_ease=0.0,
                flesch_kincaid_grade=0.0,
                automated_readability_index=0.0,
                coleman_liau_index=0.0,
                reading_level="不明",
                difficulty_assessment="分析不可",
            )

        # 基本指標
        total_words = len(words)
        total_sentences = len(sentences)
        total_syllables = sum(self._count_syllables(word) for word in words)
        total_characters = sum(len(word) for word in words)

        # Flesch Reading Ease
        flesch_ease = (
            206.835
            - (1.015 * (total_words / total_sentences))
            - (84.6 * (total_syllables / total_words))
        )

        # Flesch-Kincaid Grade Level
        flesch_grade = (
            (0.39 * (total_words / total_sentences))
            + (11.8 * (total_syllables / total_words))
            - 15.59
        )

        # Automated Readability Index
        ari = (
            (4.71 * (total_characters / total_words))
            + (0.5 * (total_words / total_sentences))
            - 21.43
        )

        # Coleman-Liau Index
        letters_per_100_words = (total_characters / total_words) * 100
        sentences_per_100_words = (total_sentences / total_words) * 100
        coleman_liau = (
            (0.0588 * letters_per_100_words) - (0.296 * sentences_per_100_words) - 15.8
        )

        # 読書レベル判定
        avg_grade = (flesch_grade + ari + coleman_liau) / 3
        if avg_grade <= 6:
            reading_level = "小学生レベル"
            difficulty = "非常に読みやすい"
        elif avg_grade <= 9:
            reading_level = "中学生レベル"
            difficulty = "読みやすい"
        elif avg_grade <= 12:
            reading_level = "高校生レベル"
            difficulty = "やや読みにくい"
        elif avg_grade <= 16:
            reading_level = "大学生レベル"
            difficulty = "読みにくい"
        else:
            reading_level = "大学院レベル"
            difficulty = "非常に読みにくい"

        return TextReadabilityEntity(
            flesch_reading_ease=flesch_ease,
            flesch_kincaid_grade=flesch_grade,
            automated_readability_index=ari,
            coleman_liau_index=coleman_liau,
            reading_level=reading_level,
            difficulty_assessment=difficulty,
        )

    @private
    async def _analyze_sentiment(self, text: str) -> TextSentimentEntity:
        """
        感情分析を実行する（簡易版）

        Args:
            text: テキスト

        Returns:
            感情分析結果
        """

        # 英語は小文字化、日本語はそのまま
        words = self._extract_words(text)

        # 感情分析のために、英語単語のみ小文字化
        processed_words = []
        for word in words:
            if re.match(r"^[a-zA-Z]+$", word):
                processed_words.append(word.lower())
            else:
                processed_words.append(word)

        positive_count = sum(
            1 for word in processed_words if word in self._positive_words
        )
        negative_count = sum(
            1 for word in processed_words if word in self._negative_words
        )
        total_emotional_words = positive_count + negative_count

        # 極性スコア計算
        if total_emotional_words == 0:
            polarity = 0.0
            sentiment_label = "neutral"
            confidence = 0.5
        else:
            polarity = (positive_count - negative_count) / total_emotional_words
            if polarity > 0.1:
                sentiment_label = "positive"
            elif polarity < -0.1:
                sentiment_label = "negative"
            else:
                sentiment_label = "neutral"

            confidence = min(total_emotional_words / max(len(words), 1) * 10, 1.0)

        # 主観性スコア（感情的な単語の割合）
        subjectivity = total_emotional_words / max(len(words), 1)

        # 感情的キーワード抽出
        emotional_keywords = [
            word
            for word in processed_words
            if word in self._positive_words or word in self._negative_words
        ]

        return TextSentimentEntity(
            polarity=polarity,
            subjectivity=subjectivity,
            sentiment_label=sentiment_label,
            confidence=confidence,
            emotional_keywords=list(set(emotional_keywords))[:10],  # 重複除去・上位10個
        )

    @private
    async def _detect_language(self, text: str) -> TextLanguageDetectionEntity:
        """
        言語検出を実行する（簡易版）

        Args:
            text: テキスト

        Returns:
            言語検出結果
        """

        language_scores = {}
        for lang_code, pattern in self._language_patterns.items():
            matches = pattern.findall(text)
            score = len(matches) / max(len(text), 1)
            if score > 0:
                language_scores[lang_code] = score

        if not language_scores:
            # デフォルトは英語
            language_scores["en"] = 1.0

        # 信頼度で並び替え
        sorted_languages = sorted(
            language_scores.items(), key=lambda x: x[1], reverse=True
        )

        # 検出結果作成
        detected_items = [
            LanguageDetectionItemEntity(
                language=lang_code,
                language_name=self._language_names.get(lang_code, lang_code),
                confidence=min(score, 1.0),
            )
            for lang_code, score in sorted_languages[:3]  # 上位3言語
        ]

        primary_language = (
            detected_items[0]
            if detected_items
            else LanguageDetectionItemEntity(
                language="en",
                language_name="English",
                confidence=0.5,
            )
        )

        # 多言語判定（2つ以上の言語が0.1以上のスコア）
        is_multilingual = len([s for s in language_scores.values() if s >= 0.1]) >= 2

        return TextLanguageDetectionEntity(
            primary_language=primary_language,
            detected_languages=detected_items,
            is_multilingual=is_multilingual,
        )

    @private
    def _extract_words(self, text: str) -> List[str]:
        """
        テキストから単語を抽出する（日本語・英語対応）

        Args:
            text: テキスト

        Returns:
            単語リスト
        """

        # 英語の単語
        english_words = re.findall(r"\b[a-zA-Z]+\b", text)

        # 日本語の単語（より細かい分割）
        japanese_words = []

        # ひらがな・カタカナ・漢字の連続を抽出
        japanese_segments = re.findall(r"[ぁ-んァ-ヶー一-龯]+", text)

        for segment in japanese_segments:
            # 各セグメントをさらに細かく分割
            # ひらがなのみ、カタカナのみ、漢字のみの連続で分割
            sub_words = re.findall(r"[ぁ-ん]+|[ァ-ヶー]+|[一-龯]+", segment)
            japanese_words.extend(sub_words)

        # 数字
        numbers = re.findall(r"\b\d+\b", text)

        return english_words + japanese_words + numbers

    @private
    def _extract_sentences(self, text: str) -> List[str]:
        """
        テキストから文を抽出する

        Args:
            text: テキスト

        Returns:
            文リスト
        """

        # 英語・日本語の文区切り
        sentences = re.split(r"[.!?。！？]+", text)
        return [s.strip() for s in sentences if s.strip()]

    @private
    def _count_syllables(self, word: str) -> int:
        """
        単語の音節数を推定する（簡易版）

        Args:
            word: 単語

        Returns:
            音節数
        """

        if not word:
            return 0

        # 日本語の場合は文字数
        if re.search(r"[ぁ-んァ-ヶー一-龯]", word):
            return len(word)

        # 英語の場合は母音グループ数で推定
        word = word.lower()
        vowels = "aeiouy"
        syllable_count = 0
        prev_was_vowel = False

        for char in word:
            is_vowel = char in vowels
            if is_vowel and not prev_was_vowel:
                syllable_count += 1
            prev_was_vowel = is_vowel

        # 最低1音節
        return max(syllable_count, 1)
