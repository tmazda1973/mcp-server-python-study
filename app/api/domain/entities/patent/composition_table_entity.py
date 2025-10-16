from pydantic import BaseModel, Field

from .composition_item_entity import CompositionItemEntity

__all__ = [
    "CompositionTableEntity",
]


class CompositionTableEntity(BaseModel):
    """
    特許構成表エンティティ
    """

    patent_number: str | None = Field(default=None, description="特許番号")
    title: str | None = Field(default=None, description="発明の名称")
    items: list[CompositionItemEntity] = Field(
        default_factory=list,
        description="構成要素のリスト",
    )
    summary: str | None = Field(default=None, description="全体の概要")
