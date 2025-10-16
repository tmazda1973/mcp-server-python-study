from pydantic import BaseModel, Field

from .comparison_item_entity import ComparisonItemEntity

__all__ = [
    "ComparisonTableEntity",
]


class ComparisonTableEntity(BaseModel):
    """
    対比表エンティティ

    複数の特許の構成要素を対比した表
    """

    base_patent_number: str = Field(..., description="基準となる特許番号")
    compared_patent_numbers: list[str] = Field(
        default_factory=list,
        description="対比対象の特許番号リスト",
    )
    items: list[ComparisonItemEntity] = Field(
        default_factory=list,
        description="対比要素のリスト",
    )
    overall_similarity: str | None = Field(
        default=None,
        description="全体的な類似性の評価",
    )
    key_differences: list[str] = Field(
        default_factory=list,
        description="主要な相違点のリスト",
    )
    summary: str | None = Field(
        default=None,
        description="対比の総括",
    )
