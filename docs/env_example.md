# 環境変数設定例

**MCPサーバーはステートレス設計のため、主な認証方式はIP制限です。**

## IP制限を使用する場合（推奨）

### 開発環境（ローカル）

```bash
# ===== 認証設定 =====
AUTH_METHOD=ip
ALLOWED_IPS_STR=127.0.0.1,::1

# その他の設定
APP_ENV=development
LOG_LEVEL=DEBUG
MCP_REQUIRE_AUTH=false
```

### 本番環境（社内ネットワーク）

```bash
# ===== 認証設定 =====
AUTH_METHOD=ip
ALLOWED_IPS_STR=192.168.1.0/24,10.0.0.0/8

# その他の設定
APP_ENV=production
LOG_LEVEL=INFO
MCP_REQUIRE_AUTH=false
```

### Docker環境

```bash
# ===== 認証設定 =====
AUTH_METHOD=ip
ALLOWED_IPS_STR=172.17.0.0/16,172.18.0.0/16,host.docker.internal

# その他の設定
APP_ENV=development
LOG_LEVEL=DEBUG
MCP_REQUIRE_AUTH=false
```

## 認証なし（開発用）

```bash
# ===== 認証設定 =====
AUTH_METHOD=none
ALLOWED_IPS_STR=

# その他の設定
APP_ENV=development
LOG_LEVEL=DEBUG
MCP_REQUIRE_AUTH=false
```

## JWT認証を使用する場合（将来対応）

**注意**: 現在はステートレスサーバーのため、JWT認証は検証のみ対応（トークン発行は別サーバー）

```bash
# ===== JWT認証設定（RS256） =====
AUTH_METHOD=jwt
JWT_ALGORITHM=RS256
JWT_PUBLIC_KEY_PATH=keys/jwt_public.pem
# または環境変数で直接指定
# JWT_PUBLIC_KEY="-----BEGIN PUBLIC KEY-----\n..."

# その他の設定
APP_ENV=production
LOG_LEVEL=INFO
MCP_REQUIRE_AUTH=false  # ステートレスのため常にfalse
```

**JWT認証の詳細は [JWT RS256移行ガイド](./jwt_rs256_migration.md) を参照してください。**

## 設定の確認方法

### 1. ローカルで確認

```bash
docker-compose up
```

起動ログを確認:

```
INFO:app.main:🔒 IP制限有効: 2個のIPアドレスを許可
INFO:app.main:許可IPリスト: ['127.0.0.1', '192.168.1.0/24']
INFO:app.main:🔓 MCP認証: IP制限ミドルウェアで制御（AUTH_METHOD設定を参照）
```

### 2. APIでテスト

```bash
# 許可されたIPからのアクセス
curl http://localhost:8030/api/v1/info

# レスポンス例（成功）
{
  "server_name": "MCP-Server",
  "version": "1.0.0",
  "environment": "development",
  "host": "127.0.0.1",
  "port": "8000"
}

# 拒否された場合のレスポンス
{
  "detail": "Access denied: Your IP address is not allowed",
  "client_ip": "8.8.8.8"
}
```

