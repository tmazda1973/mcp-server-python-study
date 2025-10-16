"""
JWT認証サービスのテスト

RS256およびHS256方式のJWT生成・検証をテストします。
"""

from datetime import datetime, timedelta, timezone

import jwt
import pytest
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi import HTTPException

from app.api.domain.services.jwt_auth import JWTService
from app.core.config import settings


@pytest.fixture
def mock_rs256_keys():
    """RS256用のモック鍵ペア"""
    # テスト用の実際のRSA鍵ペア

    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend(),
    )

    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode("utf-8")

    public_pem = (
        private_key.public_key()
        .public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        .decode("utf-8")
    )

    return {"private_key": private_pem, "public_key": public_pem}


class TestJWTServiceRS256:
    """
    JWTServiceのRS256方式テスト
    """

    @pytest.fixture(autouse=True)
    def setup_rs256(self, monkeypatch, mock_rs256_keys):
        """RS256方式用のセットアップ"""
        monkeypatch.setattr(settings, "JWT_ALGORITHM", "RS256")
        monkeypatch.setattr(settings, "JWT_PRIVATE_KEY", mock_rs256_keys["private_key"])
        monkeypatch.setattr(settings, "JWT_PUBLIC_KEY", mock_rs256_keys["public_key"])

    def test_create_jwt_token_rs256(self):
        """
        正常系テスト: RS256でJWTトークンを生成できることを確認
        """
        jwt_service = JWTService()

        token_response = jwt_service.create_jwt_token(
            user_id="test_user_123",
            username="test_user",
            email="test@example.com",
            role="admin",
        )

        assert token_response.access_token is not None
        assert isinstance(token_response.access_token, str)
        assert token_response.user_info["user_id"] == "test_user_123"
        assert token_response.user_info["username"] == "test_user"
        assert token_response.user_info["email"] == "test@example.com"
        assert token_response.user_info["role"] == "admin"

    def test_verify_jwt_token_rs256(self):
        """
        正常系テスト: RS256で生成したJWTトークンを検証できることを確認
        """
        jwt_service = JWTService()

        # トークン生成
        token_response = jwt_service.create_jwt_token(
            user_id="test_user_123",
            username="test_user",
            email="test@example.com",
            role="user",
        )

        # トークン検証
        payload = jwt_service.verify_jwt_token(token_response.access_token)

        assert payload.sub == "test_user_123"
        assert payload.username == "test_user"
        assert payload.email == "test@example.com"
        assert payload.role == "user"
        assert isinstance(payload.exp, datetime)
        assert isinstance(payload.iat, datetime)

    def test_verify_jwt_token_expired_rs256(self, mock_rs256_keys):
        """
        異常系テスト: 期限切れトークンで例外が発生することを確認
        """
        # 期限切れトークンを生成
        now = datetime.now(timezone.utc)
        expired_time = now - timedelta(hours=1)

        payload = {
            "sub": "test_user_123",
            "username": "test_user",
            "email": "test@example.com",
            "role": "user",
            "exp": expired_time,
            "iat": now - timedelta(hours=2),
        }

        expired_token = jwt.encode(
            payload,
            mock_rs256_keys["private_key"],
            algorithm="RS256",
        )

        jwt_service = JWTService()

        with pytest.raises(HTTPException) as exc_info:
            jwt_service.verify_jwt_token(expired_token)

        assert exc_info.value.status_code == 401
        assert "expired" in exc_info.value.detail.lower()

    def test_verify_jwt_token_invalid_signature_rs256(self, mock_rs256_keys):
        """
        異常系テスト: 無効な署名のトークンで例外が発生することを確認
        """
        # 別の鍵で署名されたトークンを生成
        another_private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend(),
        )

        another_private_pem = another_private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        ).decode("utf-8")

        payload = {
            "sub": "test_user_123",
            "username": "test_user",
            "email": "test@example.com",
            "role": "user",
            "exp": datetime.now(timezone.utc) + timedelta(hours=1),
            "iat": datetime.now(timezone.utc),
        }

        invalid_token = jwt.encode(
            payload,
            another_private_pem,
            algorithm="RS256",
        )

        jwt_service = JWTService()

        with pytest.raises(HTTPException) as exc_info:
            jwt_service.verify_jwt_token(invalid_token)

        assert exc_info.value.status_code == 401

    def test_verify_jwt_token_missing_required_fields_rs256(self, mock_rs256_keys):
        """
        異常系テスト: 必須フィールドが欠けている場合に例外が発生することを確認
        """
        # subフィールドがないトークンを生成
        payload = {
            "username": "test_user",
            "email": "test@example.com",
            "role": "user",
            "exp": datetime.now(timezone.utc) + timedelta(hours=1),
            "iat": datetime.now(timezone.utc),
        }

        invalid_token = jwt.encode(
            payload,
            mock_rs256_keys["private_key"],
            algorithm="RS256",
        )

        jwt_service = JWTService()

        with pytest.raises(HTTPException) as exc_info:
            jwt_service.verify_jwt_token(invalid_token)

        assert exc_info.value.status_code == 401
        assert "Invalid token payload" in exc_info.value.detail

    def test_create_jwt_token_with_custom_expiration_rs256(self):
        """
        正常系テスト: カスタム有効期限でトークンを生成できることを確認
        """
        jwt_service = JWTService()

        custom_expiration = timedelta(minutes=30)
        token_response = jwt_service.create_jwt_token(
            user_id="test_user_123",
            username="test_user",
            expires_delta=custom_expiration,
        )

        # トークンを検証して有効期限を確認
        payload = jwt_service.verify_jwt_token(token_response.access_token)

        # 有効期限がおおよそ30分後であることを確認（±1分の誤差を許容）
        expected_exp = datetime.now(timezone.utc) + custom_expiration
        time_diff = abs((payload.exp - expected_exp).total_seconds())
        assert time_diff < 60  # 1分以内の誤差

    def test_load_private_key_from_file(self, monkeypatch, mock_rs256_keys, tmp_path):
        """
        正常系テスト: ファイルから秘密鍵を読み込めることを確認
        """
        # 環境変数をクリア
        monkeypatch.setattr(settings, "JWT_PRIVATE_KEY", None)
        monkeypatch.setattr(settings, "JWT_PUBLIC_KEY", None)

        # 一時ファイルを作成
        private_key_file = tmp_path / "jwt_private.pem"
        public_key_file = tmp_path / "jwt_public.pem"

        private_key_file.write_text(mock_rs256_keys["private_key"])
        public_key_file.write_text(mock_rs256_keys["public_key"])

        monkeypatch.setattr(settings, "JWT_PRIVATE_KEY_PATH", str(private_key_file))
        monkeypatch.setattr(settings, "JWT_PUBLIC_KEY_PATH", str(public_key_file))

        jwt_service = JWTService()

        # トークン生成・検証が正常に動作することを確認
        token_response = jwt_service.create_jwt_token(
            user_id="test_user_123",
            username="test_user",
        )
        payload = jwt_service.verify_jwt_token(token_response.access_token)

        assert payload.sub == "test_user_123"

    def test_load_private_key_file_not_found(self, monkeypatch):
        """
        異常系テスト: 秘密鍵ファイルが存在しない場合に例外が発生することを確認
        """
        monkeypatch.setattr(settings, "JWT_PRIVATE_KEY", None)
        monkeypatch.setattr(settings, "JWT_PUBLIC_KEY", None)
        monkeypatch.setattr(settings, "JWT_PRIVATE_KEY_PATH", "nonexistent.pem")
        monkeypatch.setattr(settings, "JWT_PUBLIC_KEY_PATH", "nonexistent.pem")

        with pytest.raises(ValueError, match="JWT秘密鍵ファイルが見つかりません"):
            JWTService()


class TestJWTServiceHS256:
    """
    JWTServiceのHS256方式テスト（既存機能の互換性確認）
    """

    @pytest.fixture(autouse=True)
    def setup_hs256(self, monkeypatch):
        """HS256方式用のセットアップ"""
        monkeypatch.setattr(settings, "JWT_ALGORITHM", "HS256")
        monkeypatch.setattr(
            settings, "JWT_SECRET_KEY", "test-secret-key-for-hs256-testing"
        )

    def test_create_jwt_token_hs256(self):
        """
        正常系テスト: HS256でJWTトークンを生成できることを確認
        """
        jwt_service = JWTService()

        token_response = jwt_service.create_jwt_token(
            user_id="test_user_123",
            username="test_user",
            email="test@example.com",
            role="user",
        )

        assert token_response.access_token is not None
        assert isinstance(token_response.access_token, str)

    def test_verify_jwt_token_hs256(self):
        """
        正常系テスト: HS256で生成したJWTトークンを検証できることを確認
        """
        jwt_service = JWTService()

        # トークン生成
        token_response = jwt_service.create_jwt_token(
            user_id="test_user_123",
            username="test_user",
        )

        # トークン検証
        payload = jwt_service.verify_jwt_token(token_response.access_token)

        assert payload.sub == "test_user_123"
        assert payload.username == "test_user"
