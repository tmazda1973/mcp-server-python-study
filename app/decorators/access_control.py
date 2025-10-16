"""
アクセス制御デコレータ

accessifyの代替として、プロジェクト独自のアクセス制御デコレータを提供します。
実際のアクセス制御は行わず、マーカーとしてのみ機能します。
"""

from typing import Any, Callable, TypeVar

F = TypeVar("F", bound=Callable[..., Any])

__all__ = [
    "private",
    "protected",
]


def private(func: F) -> F:
    """
    プライベートメソッド用デコレータ

    accessifyの@privateの代替として使用します。
    実際のアクセス制御は行わず、マーカーとしてのみ機能します。

    Args:
        func: デコレートする関数

    Returns:
        デコレートされた関数

    Example:
        class MyClass:
            @private
            def _internal_method(self):
                return "private"
    """
    func._is_private = True
    func.__doc__ = f"[PRIVATE] {func.__doc__ or ''}"
    return func


def protected(func: F) -> F:
    """
    プロテクトメソッド用デコレータ

    Args:
        func: デコレートする関数

    Returns:
        デコレートされた関数

    Example:
        class MyClass:
            @protected
            def _protected_method(self):
                return "protected"
    """
    func._is_protected = True
    func.__doc__ = f"[PROTECTED] {func.__doc__ or ''}"
    return func
