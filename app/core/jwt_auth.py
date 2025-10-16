"""
JWT認証機能

Webアプリケーション向けJWT認証の実装
- JWTトークン生成・検証
- Bearer Token認証
- ユーザー情報管理

このファイルはFastAPI依存関係とドメインサービスの橋渡しを行う
"""

from datetime import timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.api.domain.entities.jwt_auth import JWTPayload, JwtToken
from app.api.domain.services.jwt_auth import JWTService, PasswordService

__all__ = [
    "JWTPayload",
    "JwtToken",
    "create_jwt_token",
    "verify_jwt_token",
    "get_current_user",
    "get_admin_user",
    "hash_password",
    "verify_password",
    "security",
]

# Bearer Token認証スキーム
security = HTTPBearer(auto_error=False)

# サービスインスタンス
_jwt_service = JWTService()
_password_service = PasswordService()


def hash_password(password: str) -> str:
    """
    パスワードをハッシュ化する

    Args:
        password: パスワード

    Returns:
        ハッシュ化されたパスワード
    """
    return _password_service.hash_password(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    パスワードを検証する

    Args:
        plain_password: 平文パスワード
        hashed_password: ハッシュ化されたパスワード

    Returns:
        True パスワードが一致する, False パスワードが一致しない
    """
    return _password_service.verify_password(
        plain_password=plain_password,
        hashed_password=hashed_password,
    )


def create_jwt_token(
    user_id: str,
    username: str,
    email: Optional[str] = None,
    role: str = "user",
    expires_delta: Optional[timedelta] = None,
) -> JwtToken:
    """
    JWTトークンを生成する

    Args:
        user_id: ユーザーID
        username: ユーザー名
        email: メールアドレス
        role: ユーザーロール
        expires_delta: 有効期限

    Returns:
        JWTトークン
    """
    return _jwt_service.create_jwt_token(
        user_id=user_id,
        username=username,
        email=email,
        role=role,
        expires_delta=expires_delta,
    )


def verify_jwt_token(token: str) -> JWTPayload:
    """JWTトークンを検証する"""
    return _jwt_service.verify_jwt_token(token)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> JWTPayload:
    """
    現在のユーザーを取得する（JWT認証）

    Args:
        credentials: Bearer Token認証情報

    Returns:
        認証されたユーザー情報

    Raises:
        HTTPException: 認証失敗時
    """

    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bearer token required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return verify_jwt_token(credentials.credentials)


async def get_admin_user(
    current_user: JWTPayload = Depends(get_current_user),
) -> JWTPayload:
    """
    管理者ユーザーを取得する

    - 管理者権限が必要なエンドポイント用

    Args:
        current_user: 現在のユーザー

    Returns:
        管理者ユーザー情報

    Raises:
        HTTPException: 管理者権限が必要な場合
    """

    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )

    return current_user
