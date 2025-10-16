from pydantic import BaseModel, Field

__all__ = [
    "ComparisonItemEntity",
]


class ComparisonItemEntity(BaseModel):
    """
    対比要素エンティティ

    複数の特許の構成要素を対比するための要素
    """

    item_number: str = Field(..., description="構成要素番号（例: 1, 1-1, 1-2）")
    base_description: str = Field(..., description="基準となる構成要素の説明")
    comparisons: dict[str, str] = Field(
        default_factory=dict,
        description="他の特許との対比（特許番号: 対応する構成要素の説明）",
    )
    similarity_notes: str | None = Field(
        default=None,
        description="類似点・相違点のメモ",
    )
