from pydantic import BaseModel, Field

from .product_comparison_item_entity import ProductComparisonItemEntity

__all__ = [
    "ProductComparisonTableEntity",
]


class ProductComparisonTableEntity(BaseModel):
    """
    製品対比表エンティティ

    特許の構成要素と自社製品の機能を対比した表
    """

    patent_number: str = Field(..., description="対比対象の特許番号")
    patent_title: str | None = Field(default=None, description="特許の名称")
    product_name: str = Field(..., description="自社製品名")
    product_version: str | None = Field(default=None, description="製品バージョン")
    items: list[ProductComparisonItemEntity] = Field(
        default_factory=list,
        description="製品対比要素のリスト",
    )
    overall_risk_assessment: str | None = Field(
        default=None,
        description="全体的なリスク評価",
    )
    implemented_features_count: int | None = Field(
        default=None,
        description="実装されている機能の数",
    )
    total_features_count: int | None = Field(
        default=None,
        description="全機能の数",
    )
    recommendations: list[str] = Field(
        default_factory=list,
        description="推奨事項のリスト",
    )
    summary: str | None = Field(
        default=None,
        description="対比の総括",
    )
