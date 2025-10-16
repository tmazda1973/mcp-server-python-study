from dataclasses import dataclass

__all__ = [
    "TextBasicStatsEntity",
]


@dataclass(frozen=True)
class TextBasicStatsEntity:
    """
    ドメインエンティティ（テキスト基本統計情報）
    """

    total_characters: int
    total_characters_no_spaces: int
    total_lines: int
    total_paragraphs: int
    total_words: int
    total_sentences: int
    average_words_per_sentence: float
    average_characters_per_word: float
    longest_word: str
    longest_sentence_length: int
