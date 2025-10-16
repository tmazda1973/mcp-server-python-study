from pydantic import BaseModel, Field

__all__ = [
    "CompositionItemEntity",
]


class CompositionItemEntity(BaseModel):
    """
    構成要素エンティティ
    """

    item_number: str = Field(..., description="構成要素番号（例: 1, 1-1, 1-2）")
    description: str = Field(..., description="構成要素の説明")
    reference_numbers: list[str] = Field(
        default_factory=list,
        description="参照符号のリスト（例: ['10', '11', '12']）",
    )
