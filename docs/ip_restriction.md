# IP制限機能

## 概要

MCP ServerにIP制限機能を実装し、特定のIPアドレスからのアクセスのみを許可する認証方式を提供します。

**ステートレスサーバーのため、IP制限が主な認証方式です。**

## 主な機能

### 1. IP制限ミドルウェア

- **ファイル**: `app/middlewares/ip_restriction_middleware.py`
- **クラス**: `IPRestrictionMiddleware`

#### 特徴

- ✅ **CIDR表記対応**: `192.168.1.0/24`のような範囲指定が可能
- ✅ **プロキシ対応**: `X-Forwarded-For`、`X-Real-IP`ヘッダーに対応
- ✅ **ヘルスチェック除外**: `/health`エンドポイントは制限対象外
- ✅ **柔軟な設定**: 環境変数で簡単に切り替え可能

### 2. 認証方式の切り替え

環境変数`AUTH_METHOD`で認証方式を切り替えることができます。

| 認証方式 | 値 | 説明 |
|---------|-----|------|
| IP制限 | `ip` | 特定のIPアドレスからのみアクセス許可（推奨） |
| JWT認証 | `jwt` | JWTトークンによる認証（将来対応、検証のみ） |
| 認証なし | `none` | 全てのアクセスを許可（開発環境用） |

**注意**: API Key認証はDB依存のため削除されました（ステートレス化）

## 設定方法

### 環境変数

`.env`ファイルに以下の設定を追加します。

```bash
# 認証方式
AUTH_METHOD=ip

# 許可するIPアドレス（カンマ区切り）
ALLOWED_IPS_STR=127.0.0.1,192.168.1.0/24,10.0.0.0/8
```

### 設定例

#### 1. ローカル開発環境（IP制限なし）

```bash
AUTH_METHOD=none
ALLOWED_IPS_STR=
```

#### 2. 社内ネットワークのみ許可

```bash
AUTH_METHOD=ip
ALLOWED_IPS_STR=192.168.1.0/24,10.0.0.0/8
```

#### 3. 特定のIPアドレスのみ許可

```bash
AUTH_METHOD=ip
ALLOWED_IPS_STR=203.0.113.1,198.51.100.1
```

#### 4. Docker環境（ホストマシンからのアクセス許可）

```bash
AUTH_METHOD=ip
ALLOWED_IPS_STR=172.17.0.0/16,host.docker.internal
```

## 使い方

### 1. IP制限の有効化

`docker-compose.yml`で環境変数を設定します。

```yaml
services:
  app:
    environment:
      - AUTH_METHOD=ip
      - ALLOWED_IPS_STR=127.0.0.1,192.168.1.0/24
```

### 2. アプリケーションの起動

```bash
docker-compose up -d
```

### 3. ログの確認

起動時にIP制限の設定が表示されます。

```
INFO:app.main:🔒 IP制限有効: 2個のIPアドレスを許可
INFO:app.main:許可IPリスト: ['127.0.0.1', '192.168.1.0/24']
INFO:app.main:🔓 MCP認証: IP制限ミドルウェアで制御（AUTH_METHOD設定を参照）
```

### 4. アクセステスト

#### 許可されたIPからのアクセス

```bash
# 127.0.0.1 からのアクセス（許可）
curl http://localhost:8030/api/v1/info
# => 200 OK
```

#### 許可されていないIPからのアクセス

```bash
# 8.8.8.8 からのアクセス（拒否）
# => 403 Forbidden
# {
#   "detail": "Access denied: Your IP address is not allowed",
#   "client_ip": "8.8.8.8"
# }
```

## CIDR表記について

CIDR（Classless Inter-Domain Routing）表記を使用すると、IPアドレスの範囲を指定できます。

### 表記例

| CIDR表記 | 説明 | IPアドレス範囲 |
|---------|------|---------------|
| `192.168.1.0/24` | クラスC (256個) | `192.168.1.0` ~ `192.168.1.255` |
| `192.168.0.0/16` | クラスB (65,536個) | `192.168.0.0` ~ `192.168.255.255` |
| `10.0.0.0/8` | クラスA (16,777,216個) | `10.0.0.0` ~ `10.255.255.255` |
| `172.16.0.0/12` | Dockerデフォルト | `172.16.0.0` ~ `172.31.255.255` |

### 計算方法

- `/32`: 単一IP（1個）
- `/24`: 256個のIP（最後のオクテット）
- `/16`: 65,536個のIP（最後の2つのオクテット）
- `/8`: 16,777,216個のIP（最後の3つのオクテット）

## プロキシ経由のアクセス

### X-Forwarded-For ヘッダー

プロキシやロードバランサー経由でアクセスする場合、`X-Forwarded-For`ヘッダーから実際のクライアントIPを取得します。

```
X-Forwarded-For: 203.0.113.1, 198.51.100.1
```

ミドルウェアは最初のIP（`203.0.113.1`）を使用します。

### X-Real-IP ヘッダー

Nginxなどのリバースプロキシでは`X-Real-IP`ヘッダーも使用されます。

```
X-Real-IP: 203.0.113.1
```

### 優先順位

1. `X-Forwarded-For`（最優先）
2. `X-Real-IP`
3. `request.client.host`（直接接続）

## テスト

テストファイル: `tests/middlewares/test_ip_restriction_middleware.py`

```bash
# テスト実行
pytest tests/middlewares/test_ip_restriction_middleware.py -v

# カバレッジ付きテスト
pytest tests/middlewares/test_ip_restriction_middleware.py --cov=app/middlewares
```

### テストケース

- ✅ 単一IPアドレスのパース
- ✅ CIDR表記のパース
- ✅ 複数IPアドレスのパース
- ✅ 無効なIPアドレスの処理
- ✅ IP許可判定（単一IP）
- ✅ IP許可判定（CIDR範囲）
- ✅ クライアントIP取得（直接接続）
- ✅ クライアントIP取得（X-Forwarded-For）
- ✅ クライアントIP取得（X-Real-IP）
- ✅ ヘルスチェックのバイパス
- ✅ 許可IPリストが空の場合
- ✅ 許可されたIPからのアクセス
- ✅ 拒否されたIPからのアクセス

## トラブルシューティング

### 1. ローカルからアクセスできない

**症状**: `localhost`や`127.0.0.1`からアクセスしても403エラー

**解決策**: `ALLOWED_IPS_STR`に`127.0.0.1`を追加

```bash
ALLOWED_IPS_STR=127.0.0.1,::1
```

### 2. Docker環境でホストからアクセスできない

**症状**: ホストマシンからコンテナにアクセスできない

**解決策**: Dockerのデフォルトネットワーク範囲を追加

```bash
ALLOWED_IPS_STR=172.17.0.0/16,172.18.0.0/16
```

### 3. プロキシ経由でアクセスできない

**症状**: Nginxやロードバランサー経由でアクセスすると403エラー

**解決策**: プロキシのIPアドレスではなく、`X-Forwarded-For`ヘッダーを設定

```nginx
# Nginx設定例
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
proxy_set_header X-Real-IP $remote_addr;
```

### 4. ログで確認する

```bash
# デバッグモードで起動
LOG_LEVEL=DEBUG docker-compose up

# ログを確認
docker logs ak-mcp-server -f
```

ログ出力例:

```
DEBUG:app.middlewares.ip_restriction_middleware:IPアドレス許可: 127.0.0.1 - /api/v1/info
WARNING:app.middlewares.ip_restriction_middleware:IPアドレス制限により拒否されました: 8.8.8.8 - /api/v1/test
```

## セキュリティ上の注意

### 1. 本番環境での設定

- ✅ 必要最小限のIPアドレスのみ許可
- ✅ 定期的な見直し（不要なIPの削除）
- ✅ ログの監視（不正アクセスの検知）

### 2. プロキシ経由の注意点

- ⚠️ `X-Forwarded-For`は偽装可能
- ✅ 信頼できるプロキシからのヘッダーのみ使用
- ✅ プロキシのIPアドレスも制限対象に含める

### 3. 多層防御

- ✅ IP制限（現在実装済み）
- ✅ JWT認証の併用（将来対応、検証のみ）
- ✅ ファイアウォールとの併用
- ✅ レート制限の実装（将来対応）

## 将来の拡張

- [ ] IPv6対応の強化
- [ ] ジオロケーション（国別制限）
- [ ] レート制限との統合
- [ ] JWT認証との併用（検証機能）
- [ ] 監視・アラート機能

**注意**: ステートレス設計のため、動的IP許可リストやDB連携は実装しません。
