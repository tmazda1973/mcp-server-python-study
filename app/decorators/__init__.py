"""
カスタムデコレータモジュール

プロジェクト専用のデコレータを提供します。
accessifyの代替として、シンプルで問題のないデコレータを実装。
"""

from .access_control import private, protected

__all__ = [
    "private",
    "protected",
]
