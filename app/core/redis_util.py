"""
Redis接続とユーティリティ関数

将来の拡張用にRedis接続を準備
- JWTトークンブラックリスト
- レート制限
- セッション管理
- キャッシュ
"""

from typing import Optional

import redis.asyncio as redis
from redis.asyncio import Redis

from app.core.config import settings

__all__ = [
    "get_redis",
    "redis_client",
]

# Redis接続インスタンス（グローバル）
redis_client: Optional[Redis] = None


async def get_redis() -> Optional[Redis]:
    """
    Redis接続を取得する

    Returns:
        Redis | None: Redis接続インスタンス、設定されていない場合はNone
    """
    global redis_client

    if not settings.REDIS_URL:
        return None

    if redis_client is None:
        try:
            redis_client = redis.from_url(
                settings.REDIS_URL,
                password=settings.REDIS_PASSWORD,
                db=settings.REDIS_DB,
                max_connections=settings.REDIS_MAX_CONNECTIONS,
                decode_responses=True,
            )
            # 接続テスト
            await redis_client.ping()
        except Exception as e:
            print(f"Redis connection failed: {e}")
            redis_client = None

    return redis_client


async def close_redis() -> None:
    """
    Redis接続を閉じる
    """
    global redis_client
    if redis_client:
        await redis_client.close()
        redis_client = None


# 将来の拡張用ヘルパー関数


async def cache_set(key: str, value: str, expire: int = 300) -> bool:
    """
    キャッシュに値を設定

    Args:
        key: キー
        value: 値
        expire: 有効期限（秒）

    Returns:
        bool: 成功したかどうか
    """
    redis_conn = await get_redis()
    if not redis_conn:
        return False

    try:
        await redis_conn.setex(key, expire, value)
        return True
    except Exception:
        return False


async def cache_get(key: str) -> Optional[str]:
    """
    キャッシュから値を取得

    Args:
        key: キー

    Returns:
        str | None: 値、存在しない場合はNone
    """
    redis_conn = await get_redis()
    if not redis_conn:
        return None

    try:
        return await redis_conn.get(key)
    except Exception:
        return None


async def cache_delete(key: str) -> bool:
    """
    キャッシュから値を削除

    Args:
        key: キー

    Returns:
        bool: 削除されたかどうか
    """
    redis_conn = await get_redis()
    if not redis_conn:
        return False

    try:
        result = await redis_conn.delete(key)
        return result > 0
    except Exception:
        return False


# レート制限用ヘルパー関数


async def rate_limit_check(user_id: str, limit: int = 100, window: int = 3600) -> bool:
    """
    レート制限チェック

    Args:
        user_id: ユーザーID
        limit: 制限回数
        window: 時間窓（秒）

    Returns:
        bool: 制限内かどうか
    """
    redis_conn = await get_redis()
    if not redis_conn:
        return True  # Redisが無効な場合は制限なし

    try:
        key = f"rate_limit:{user_id}"
        current = await redis_conn.incr(key)
        if current == 1:
            await redis_conn.expire(key, window)
        return current <= limit
    except Exception:
        return True  # エラー時は制限なし


# JWTブラックリスト用ヘルパー関数


async def blacklist_token(token_jti: str, expire_time: int) -> bool:
    """
    JWTトークンをブラックリストに追加

    Args:
        token_jti: JWT ID
        expire_time: 有効期限（秒）

    Returns:
        bool: 成功したかどうか
    """
    redis_conn = await get_redis()
    if not redis_conn:
        return False

    try:
        await redis_conn.setex(f"blacklist:{token_jti}", expire_time, "1")
        return True
    except Exception:
        return False


async def is_token_blacklisted(token_jti: str) -> bool:
    """
    JWTトークンがブラックリストに登録されているかチェック

    Args:
        token_jti: JWT ID

    Returns:
        bool: ブラックリストに登録されているかどうか
    """
    redis_conn = await get_redis()
    if not redis_conn:
        return False  # Redisが無効な場合はブラックリストなし

    try:
        result = await redis_conn.exists(f"blacklist:{token_jti}")
        return result > 0
    except Exception:
        return False
