"""
パスワード認証サービス
"""

from passlib.context import CryptContext

__all__ = [
    "PasswordService",
]


class PasswordService:
    """
    パスワード認証サービス

    パスワードのハッシュ化と検証を行う
    """

    def __init__(self) -> None:
        """
        コンストラクタ
        """
        self._pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def hash_password(self, password: str) -> str:
        """
        パスワードをハッシュ化する

        Args:
            password: 平文パスワード

        Returns:
            str: ハッシュ化されたパスワード
        """
        return self._pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        パスワードを検証する

        Args:
            plain_password: 平文パスワード
            hashed_password: ハッシュ化されたパスワード

        Returns:
            bool: パスワードが一致するかどうか
        """
        return self._pwd_context.verify(plain_password, hashed_password)
