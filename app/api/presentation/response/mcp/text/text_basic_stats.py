from pydantic import BaseModel, Field

__all__ = [
    "TextBasicStats",
]


class TextBasicStats(BaseModel):
    """
    テキスト基本統計情報
    """

    total_characters: int = Field(
        ...,
        description="総文字数",
    )
    total_characters_no_spaces: int = Field(
        ...,
        description="空白を除く文字数",
    )
    total_lines: int = Field(
        ...,
        description="総行数",
    )
    total_paragraphs: int = Field(
        ...,
        description="総段落数",
    )
    total_words: int = Field(
        ...,
        description="総単語数",
    )
    total_sentences: int = Field(
        ...,
        description="総文数",
    )
    average_words_per_sentence: float = Field(
        ...,
        description="文あたりの平均単語数",
    )
    average_characters_per_word: float = Field(
        ...,
        description="単語あたりの平均文字数",
    )
    longest_word: str = Field(
        ...,
        description="最長単語",
    )
    longest_sentence_length: int = Field(
        ...,
        description="最長文の文字数",
    )
