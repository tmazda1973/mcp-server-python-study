"""
依存性注入（ドメイン層）
"""

from app.api.domain.services.jwt_auth import JWTService, PasswordService

__all__ = [
    "provide_jwt_service",
    "provide_password_service",
]


def provide_jwt_service() -> JWTService:
    """
    JWTサービスを提供する
    """
    return JWTService()


def provide_password_service() -> PasswordService:
    """
    パスワード認証サービスを提供する
    """
    return PasswordService()
