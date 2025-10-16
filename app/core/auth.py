"""
認証関連のヘルパー関数

Note:
    DB依存の認証機能は削除済み（ステートレス化）
    将来的に必要になった場合は、system-serverから認証情報を取得する設計に変更
"""

# import hashlib
#
# from fastapi import Depends, HTTPException, status
# from fastapi.security import APIKeyHeader, HTTPBearer
# from sqlalchemy.orm import Session
#
# from app.core.config import settings
# from app.database import get_db
# from app.models.auth.api_key import APIKey

__all__ = [
    # "verify_api_key",  # DB依存のため削除
]


# # 認証設定
# API_KEY_NAME = settings.API_KEY_NAME
#
# # Bearer Token認証を使用するためのSchemeを定義
# bearer_token_auth_scheme = HTTPBearer()
#
# # Header 受け取り用 Security 依存定義
# api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)
#
#
# async def verify_api_key(
#     api_key: str | None = Depends(api_key_header),
#     db: Session = Depends(get_db),
# ) -> dict:
#     """
#     APIキーを検証する（Stripe方式）
#
#     APIキー形式: {key_id}.{secret}
#     例: ak_abc123.xyz789
#
#     Args:
#         api_key: APIキー
#         db: データベースセッション
#
#     Returns:
#         dict: APIキー情報（key_id, user_id等）
#
#     Raises:
#         HTTPException: APIキーが無効な場合
#
#     Note:
#         MCP_REQUIRE_AUTH=falseの場合、認証をスキップする
#     """
#
#     # MCP認証が無効の場合はスキップ
#     if not settings.MCP_REQUIRE_AUTH:
#         return {"key_id": "mcp-auth-disabled", "user_id": None}
#
#     # APIキーが提供されていない場合
#     if not api_key:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="API Key is required",
#             headers={"WWW-Authenticate": "APIKey"},
#         )
#
#     # APIキーをパース（Stripe方式: {key_id}.{secret}）
#     try:
#         parts = api_key.split(".", 1)  # ドットで2分割
#         if len(parts) != 2:
#             raise ValueError("Invalid API key format")
#
#         key_id = parts[0]  # key_id部分（"ak_" プレフィックス含む）
#         secret = parts[1]  # secret部分
#
#         # key_idがak_で始まることを確認
#         if not key_id.startswith("ak_"):
#             raise ValueError("Invalid API key format")
#     except (ValueError, IndexError):
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid API Key format",
#         ) from None
#
#     # APIキーを検証する
#     db_api_key = db.query(APIKey).filter(APIKey.key_id == key_id).first()
#     if not db_api_key:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid API Key",
#         )
#
#     # アクティブ状態チェック
#     if not db_api_key.is_active:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="API Key is inactive",
#         )
#
#     # 有効期限チェック
#     if db_api_key.expires_at:
#         from datetime import datetime, timezone
#
#         if datetime.now(timezone.utc) > db_api_key.expires_at:
#             raise HTTPException(
#                 status_code=status.HTTP_401_UNAUTHORIZED,
#                 detail="API Key has expired",
#             )
#
#     # シークレット部分をハッシュ化して照合
#     secret_hash = hashlib.sha256(secret.encode()).hexdigest()
#     if secret_hash != db_api_key.key_hash:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid API Key",
#         )
#
#     # 使用回数を更新する
#     db_api_key.usage_count += 1
#     db.commit()
#
#     # APIキー情報を返す
#     return {
#         "key_id": db_api_key.key_id,
#         "user_id": db_api_key.user_id,
#         "name": db_api_key.name,
#     }
