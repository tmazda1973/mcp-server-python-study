from pydantic import BaseModel, Field

__all__ = [
    "ProductComparisonItemEntity",
]


class ProductComparisonItemEntity(BaseModel):
    """
    製品対比要素エンティティ

    特許の構成要素と自社製品の機能を対比するための要素
    """

    item_number: str = Field(..., description="構成要素番号（例: 1, 1-1, 1-2）")
    patent_description: str = Field(..., description="特許の構成要素の説明")
    product_feature: str | None = Field(
        default=None,
        description="対応する製品の機能・特徴",
    )
    is_implemented: bool = Field(..., description="製品に実装されているか")
    implementation_notes: str | None = Field(
        default=None,
        description="実装状況の詳細メモ",
    )
    infringement_risk: str | None = Field(
        default=None,
        description="侵害リスク評価（高/中/低/なし）",
    )
