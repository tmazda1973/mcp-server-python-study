from datetime import datetime
from typing import Optional

from pydantic import BaseModel

__all__ = [
    "JWTPayload",
]


class JWTPayload(BaseModel):
    """
    JWTペイロードエンティティ

    - JWTトークンに含まれるユーザー情報
    """

    sub: str  # ユーザーID
    username: str
    email: Optional[str] = None
    role: str = "user"
    exp: datetime
    iat: datetime
