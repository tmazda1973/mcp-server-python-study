from typing import List, Optional

from pydantic import BaseModel, Field

from .text_replace_match import TextReplaceMatch

__all__ = [
    "TextReplaceResponse",
]


class TextReplaceResponse(BaseModel):
    """
    レスポンスデータ（テキスト置換ツール）
    """

    success: bool = Field(..., description="置換実行成功")
    pattern: str = Field(..., description="使用された検索パターン")
    replacement: str = Field(..., description="使用された置換文字列")
    total_replacements: int = Field(..., description="総置換数")
    total_lines: int = Field(..., description="処理対象の総行数")
    modified_lines: int = Field(..., description="変更された行数")
    matches: List[TextReplaceMatch] = Field(..., description="置換結果一覧")
    result_text: str = Field(..., description="置換後のテキスト全体")
    truncated: bool = Field(..., description="結果が切り詰められたか")
    preview_only: bool = Field(..., description="プレビューモードか")
    processing_time: float = Field(..., description="処理実行時間（秒）")
    case_sensitive: bool = Field(..., description="大文字小文字区別設定")
    use_regex: bool = Field(..., description="正規表現使用設定")
    whole_word: bool = Field(..., description="単語全体マッチ設定")
    error: Optional[str] = Field(default=None, description="エラーメッセージ")
    warning: Optional[str] = Field(default=None, description="警告メッセージ")
