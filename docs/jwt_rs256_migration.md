# JWT認証のRS256移行ガイド

## 概要

JWT認証をHS256（共有鍵方式）からRS256（公開鍵/秘密鍵方式）に移行しました。これにより、よりセキュアで拡張性の高い認証システムを実現します。

## 主な変更点

### 1. アルゴリズムの変更

| 項目 | Before (HS256) | After (RS256) |
|------|----------------|---------------|
| 鍵の種類 | 共有鍵（対称鍵） | 公開鍵/秘密鍵（非対称鍵） |
| 鍵の管理 | 1つのシークレットキー | 秘密鍵と公開鍵のペア |
| トークン署名 | シークレットキーで署名 | 秘密鍵で署名 |
| トークン検証 | シークレットキーで検証 | 公開鍵で検証 |
| セキュリティ | 鍵が漏洩すると署名・検証両方が危険 | 秘密鍵が漏洩しても検証は安全 |

### 2. DB非依存化

- Redis依存を削除
- 完全にステートレスな認証システム
- 水平スケーリングが容易

### 3. 新しい設定項目

```python
# app/core/config.py
JWT_ALGORITHM: str = "RS256"  # RS256 または HS256
JWT_PRIVATE_KEY_PATH: str = "keys/jwt_private.pem"
JWT_PUBLIC_KEY_PATH: str = "keys/jwt_public.pem"
JWT_PRIVATE_KEY: Optional[str] = None  # 環境変数で直接指定
JWT_PUBLIC_KEY: Optional[str] = None   # 環境変数で直接指定
```

## セットアップ手順

### 1. RSA鍵ペアの生成

#### 方法A: Makefileを使用（推奨）

```bash
# scripts/setup/ ディレクトリに移動
cd scripts/setup/

# デフォルト設定で生成（2048 bits）
make generate-keys

# 強制上書き
make generate-keys-force

# 4096 bitsで生成
make generate-keys-4096

# Docker環境で実行
make docker-generate-keys

# ヘルプを表示
make help
```

詳細は [`scripts/setup/README.md`](../../scripts/setup/README.md) を参照してください。

#### 方法B: opensslコマンドを使用

```bash
# 秘密鍵を生成
openssl genpkey -algorithm RSA -out keys/jwt_private.pem -pkeyopt rsa_keygen_bits:2048

# 公開鍵を生成
openssl rsa -pubout -in keys/jwt_private.pem -out keys/jwt_public.pem

# パーミッションを設定
chmod 600 keys/jwt_private.pem
chmod 644 keys/jwt_public.pem
```

### 2. 環境変数の設定

#### 開発環境（ファイルから読み込み）

```yaml
# docker-compose.yml
environment:
  - JWT_ALGORITHM=RS256
  # JWT_PRIVATE_KEY_PATH と JWT_PUBLIC_KEY_PATH はデフォルト値を使用
```

```bash
# .env
JWT_ALGORITHM=RS256
JWT_PRIVATE_KEY_PATH=keys/jwt_private.pem
JWT_PUBLIC_KEY_PATH=keys/jwt_public.pem
```

#### 本番環境（環境変数で直接指定）

```bash
# .env
JWT_ALGORITHM=RS256

# 鍵を環境変数で直接指定（推奨）
JWT_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----
MIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQC...
-----END PRIVATE KEY-----"

JWT_PUBLIC_KEY="-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEArDH+wS...
-----END PUBLIC KEY-----"
```

**本番環境での推奨事項:**
- AWS Secrets Manager、Azure Key Vault、GCP Secret Manager などを使用
- 環境変数ではなく、シークレット管理サービスから動的に取得
- 秘密鍵のローテーションを定期的に実施

### 3. アプリケーションの起動

```bash
# Docker環境
docker-compose down
docker-compose up -d

# ログで確認
docker-compose logs app | grep JWT
```

## 使い方

### JWT トークンの生成

```python
from app.core.jwt_auth import create_jwt_token

# トークン生成
token_response = create_jwt_token(
    user_id="user_123",
    username="john_doe",
    email="john@example.com",
    role="admin",
)

print(f"Access Token: {token_response.access_token}")
print(f"Expires At: {token_response.expires_at}")
```

### JWT トークンの検証

```python
from app.core.jwt_auth import verify_jwt_token

# トークン検証
try:
    payload = verify_jwt_token(token)
    print(f"User ID: {payload.sub}")
    print(f"Username: {payload.username}")
    print(f"Role: {payload.role}")
except HTTPException as e:
    print(f"Error: {e.detail}")
```

### FastAPI エンドポイントでの使用

```python
from fastapi import Depends
from app.core.jwt_auth import get_current_user, get_admin_user, JWTPayload

@app.get("/protected")
async def protected_endpoint(
    current_user: JWTPayload = Depends(get_current_user)
):
    return {"user_id": current_user.sub, "username": current_user.username}

@app.get("/admin-only")
async def admin_only_endpoint(
    admin_user: JWTPayload = Depends(get_admin_user)
):
    return {"message": "Admin access granted"}
```

## マイグレーション

### HS256からRS256への移行

既存のHS256システムからRS256に移行する手順:

#### ステップ1: RSA鍵ペアを生成

```bash
cd scripts/setup/
make generate-keys
```

#### ステップ2: 環境変数を更新

```bash
# .env
JWT_ALGORITHM=RS256  # HS256 → RS256 に変更
```

#### ステップ3: アプリケーションを再起動

```bash
docker-compose restart app
```

#### ステップ4: 既存トークンの無効化

⚠️ **重要**: アルゴリズムを変更すると、既存のJWTトークンは検証できなくなります。

対策:
1. **ダウンタイムを設ける**: メンテナンスモードに入り、全ユーザーを再ログインさせる
2. **段階的移行**: 一定期間、HS256とRS256の両方をサポートする（複雑）
3. **トークンのリフレッシュ機能**: 既存トークンを新しい形式に自動変換

## テスト

### ユニットテスト

```bash
# RS256のテストを実行
pytest tests/api/domain/services/jwt_auth/test_jwt_service.py::TestJWTServiceRS256 -v

# HS256のテストを実行（互換性確認）
pytest tests/api/domain/services/jwt_auth/test_jwt_service.py::TestJWTServiceHS256 -v

# 全テストを実行
pytest tests/api/domain/services/jwt_auth/test_jwt_service.py -v
```

### 手動テスト

```bash
# トークンを生成してデコード
curl -X POST http://localhost:8030/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password"}' \
  | jq -r '.access_token' \
  | jwt decode -
```

## トラブルシューティング

### 1. 鍵ファイルが見つからない

**エラー:**
```
ValueError: JWT秘密鍵ファイルが見つかりません: keys/jwt_private.pem
```

**解決策:**
```bash
# 鍵を生成
cd scripts/setup/
make generate-keys

# ファイルが存在することを確認
ls -la ../../keys/
```

### 2. 鍵の形式が無効

**エラー:**
```
ValueError: Could not deserialize key data.
```

**解決策:**
- PEM形式であることを確認
- ファイルが破損していないか確認
- 鍵を再生成

```bash
cd scripts/setup/
make generate-keys-force
```

### 3. トークン検証エラー

**エラー:**
```
HTTPException: Invalid token signature
```

**原因:**
- トークンが別の鍵で署名されている
- トークンが改ざんされている
- アルゴリズムが一致していない

**解決策:**
```bash
# 環境変数を確認
docker-compose exec app env | grep JWT

# 新しいトークンを発行
# クライアント側で再ログイン
```

### 4. パーミッションエラー

**エラー:**
```
PermissionError: [Errno 13] Permission denied: 'keys/jwt_private.pem'
```

**解決策:**
```bash
# パーミッションを修正
chmod 600 keys/jwt_private.pem
chmod 644 keys/jwt_public.pem
```

## セキュリティのベストプラクティス

### 1. 秘密鍵の管理

✅ **推奨:**
- 秘密鍵はバージョン管理システム（Git）に含めない
- `.gitignore` に `keys/` と `*.pem` を追加済み
- 本番環境ではシークレット管理サービスを使用
- 定期的に鍵をローテーション（3〜6ヶ月ごと）

❌ **禁止:**
- 秘密鍵をコードにハードコーディング
- 秘密鍵をログに出力
- 秘密鍵を平文でメール送信
- 秘密鍵を公開リポジトリにコミット

### 2. 鍵のサイズ

| 鍵サイズ | セキュリティレベル | 推奨用途 |
|---------|-----------------|---------|
| 2048 bits | 標準 | 一般的な用途 |
| 3072 bits | 高 | 機密性の高いデータ |
| 4096 bits | 最高 | 最高レベルのセキュリティが必要な場合 |

**推奨**: 2048 bits（セキュリティと性能のバランスが良い）

### 3. トークンの有効期限

```python
# 短い有効期限を設定（推奨: 15分〜1時間）
ACCESS_TOKEN_EXPIRE_MINUTES = 60  # 1時間

# リフレッシュトークンを別途実装（推奨: 7日〜30日）
REFRESH_TOKEN_EXPIRE_DAYS = 7
```

### 4. HTTPS通信

本番環境では必ずHTTPS通信を使用してください。トークンが平文で送信されることを防ぎます。

## パフォーマンス

### RS256 vs HS256

| 項目 | HS256 | RS256 |
|------|-------|-------|
| 署名速度 | ⚡ 高速 | 🐢 低速（約10倍遅い） |
| 検証速度 | ⚡ 高速 | ⚡ 高速 |
| 鍵のサイズ | 小（256 bits） | 大（2048+ bits） |
| セキュリティ | 良 | 優 |
| 用途 | 単一サーバー | マイクロサービス、分散システム |

**最適化のヒント:**
- トークンの検証は高速なので、API Gateway等で公開鍵のみ配布して検証可能
- 署名はAuthサービスのみで行い、他のサービスは検証のみ
- トークンのキャッシュ（必要に応じて）

## 参考資料

- [RFC 7519 - JSON Web Token (JWT)](https://tools.ietf.org/html/rfc7519)
- [RFC 7515 - JSON Web Signature (JWS)](https://tools.ietf.org/html/rfc7515)
- [PyJWT Documentation](https://pyjwt.readthedocs.io/)
- [Cryptography Documentation](https://cryptography.io/)

## 次のステップ

- [ ] リフレッシュトークンの実装
- [ ] トークンのブラックリスト機能
- [ ] 鍵のローテーション機能
- [ ] Kubernetes Secrets との統合
- [ ] JWT クレームの拡張（permissions, scopes など）
