from datetime import datetime
from typing import Any

from pydantic import BaseModel

__all__ = [
    "JwtToken",
]


class JwtToken(BaseModel):
    """
    JWTトークンエンティティ
    """

    access_token: str
    expires_at: datetime
    user_info: dict[str, Any]

    @property
    def expires_in_seconds(self) -> int:
        """
        トークンの残り有効期間（秒）を計算する

        Returns:
            int: 有効期間（秒）
        """
        now = datetime.now(self.expires_at.tzinfo)
        delta = self.expires_at - now
        return max(0, int(delta.total_seconds()))
