from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

import jwt
from fastapi import HTTPException, status

from app.api.domain.entities.jwt_auth import JWTPayload, JwtToken
from app.core.config import settings
from app.decorators.access_control import private

__all__ = [
    "JWTService",
]


class JWTService:
    """
    JWTトークンサービス

    JWTトークンの生成・検証を行う

    - HS256: 共有鍵方式（JWT_SECRET_KEYを使用）
    - RS256: 公開鍵/秘密鍵方式（JWT_PRIVATE_KEY/JWT_PUBLIC_KEYを使用）
    """

    def __init__(self) -> None:
        """
        コンストラクタ
        """
        self._algorithm = settings.JWT_ALGORITHM
        self._expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES

        # アルゴリズムに応じて鍵を読み込む
        if self._algorithm == "RS256":
            self._private_key = self._load_private_key()
            self._public_key = self._load_public_key()
            self._secret_key = None  # RS256では使用しない
        else:  # HS256
            self._secret_key = settings.JWT_SECRET_KEY
            self._private_key = None
            self._public_key = None

    @private
    def _load_private_key(self) -> str:
        """
        RS256用の秘密鍵を読み込む

        優先順位:
        1. 環境変数 JWT_PRIVATE_KEY
        2. ファイル JWT_PRIVATE_KEY_PATH

        Returns:
            秘密鍵（PEM形式）

        Raises:
            ValueError: 秘密鍵が見つからない場合
        """

        # 環境変数から読み込み（優先）
        if settings.JWT_PRIVATE_KEY:
            return settings.JWT_PRIVATE_KEY

        # ファイルから読み込み
        key_path = Path(settings.JWT_PRIVATE_KEY_PATH)
        if not key_path.exists():
            raise ValueError(
                f"JWT秘密鍵ファイルが見つかりません: {key_path}\n"
                f"scripts/generate_rsa_keys.py を実行して鍵を生成してください"
            )

        with open(key_path, "r") as f:
            return f.read()

    @private
    def _load_public_key(self) -> str:
        """
        RS256用の公開鍵を読み込む

        優先順位:
        1. 環境変数 JWT_PUBLIC_KEY
        2. ファイル JWT_PUBLIC_KEY_PATH

        Returns:
            公開鍵（PEM形式）

        Raises:
            ValueError: 公開鍵が見つからない場合
        """

        # 環境変数から読み込み（優先）
        if settings.JWT_PUBLIC_KEY:
            return settings.JWT_PUBLIC_KEY

        # ファイルから読み込み
        key_path = Path(settings.JWT_PUBLIC_KEY_PATH)
        if not key_path.exists():
            raise ValueError(
                f"JWT公開鍵ファイルが見つかりません: {key_path}\n"
                f"scripts/generate_rsa_keys.py を実行して鍵を生成してください"
            )

        with open(key_path, "r") as f:
            return f.read()

    def create_jwt_token(
        self,
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
            expires_delta: 有効期限（指定しない場合はデフォルト）

        Returns:
            TokenResponse: アクセストークンとユーザー情報
        """

        # 有効期限を設定する
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            # デフォルトの有効期限を設定する
            expire = datetime.now(timezone.utc) + timedelta(
                minutes=self._expire_minutes
            )

        # JWTトークンを生成する
        now = datetime.now(timezone.utc)
        payload = {
            "sub": user_id,
            "username": username,
            "email": email,
            "role": role,
            "exp": expire,
            "iat": now,
        }

        # アルゴリズムに応じて鍵を選択
        if self._algorithm == "RS256":
            key = self._private_key
        else:
            key = self._secret_key

        access_token = jwt.encode(
            payload,
            key,
            algorithm=self._algorithm,
        )

        return JwtToken(
            access_token=access_token,
            expires_at=expire,
            user_info={
                "user_id": user_id,
                "username": username,
                "email": email,
                "role": role,
            },
        )

    def verify_jwt_token(self, token: str) -> JWTPayload:
        """
        JWTトークンを検証する

        Args:
            token: JWTトークン

        Returns:
            JWTPayload: デコードされたペイロード

        Raises:
            HTTPException: トークンが無効な場合
        """

        try:
            # アルゴリズムに応じて鍵を選択
            if self._algorithm == "RS256":
                key = self._public_key
            else:
                key = self._secret_key

            payload = jwt.decode(
                token,
                key,
                algorithms=[self._algorithm],
            )

            # 必須フィールドの確認
            user_id = payload.get("sub")
            username = payload.get("username")
            if user_id is None or username is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token payload",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            return JWTPayload(
                sub=user_id,
                username=username,
                email=payload.get("email"),
                role=payload.get("role", "user"),
                exp=datetime.fromtimestamp(payload.get("exp"), tz=timezone.utc),
                iat=datetime.fromtimestamp(payload.get("iat"), tz=timezone.utc),
            )
        except jwt.ExpiredSignatureError as err:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            ) from err
        except jwt.InvalidSignatureError as err:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token signature",
                headers={"WWW-Authenticate": "Bearer"},
            ) from err
        except jwt.PyJWTError as err:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Could not validate token: {err}",
                headers={"WWW-Authenticate": "Bearer"},
            ) from err
