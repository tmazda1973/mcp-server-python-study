# セットアップスクリプト

MCPサーバーの初期セットアップに必要なスクリプト集

## 📁 ディレクトリ構成

```
scripts/setup/
├── README.md                   # このファイル
├── Makefile                    # セットアップタスク定義
└── generate_rsa_keys.py        # RSA鍵ペア生成スクリプト
```

## 🔑 RSA鍵ペア生成

JWT認証（RS256）用のRSA秘密鍵・公開鍵を生成します。

### 使い方

#### 1. Makefileを使う（推奨）

```bash
# scripts/setup/ ディレクトリに移動
cd scripts/setup/

# デフォルト設定で生成（2048 bits）
make generate-keys

# 強制上書き
make generate-keys-force

# 4096 bitsで生成
make generate-keys-4096

# カスタムパス指定
make generate-keys-custom PRIVATE=keys/my_private.pem PUBLIC=keys/my_public.pem

# ヘルプ表示
make help
```

#### 2. Pythonスクリプトを直接実行

```bash
# デフォルト設定で生成
python scripts/setup/generate_rsa_keys.py

# カスタムパス
python scripts/setup/generate_rsa_keys.py \
  --private-key keys/custom_private.pem \
  --public-key keys/custom_public.pem

# 鍵サイズ変更（2048, 3072, 4096 bits）
python scripts/setup/generate_rsa_keys.py --key-size 4096

# 既存ファイルを強制上書き
python scripts/setup/generate_rsa_keys.py --force

# ヘルプ表示
python scripts/setup/generate_rsa_keys.py --help
```

### Docker環境での実行

```bash
# scripts/setup/ ディレクトリに移動
cd scripts/setup/

# Makefile経由で実行（推奨）
make docker-generate-keys

# 強制上書き
make docker-generate-keys-force

# または、docker-composeコマンドで直接実行
docker-compose -f ../../docker-compose.yml exec app python scripts/setup/generate_rsa_keys.py
```

### セキュリティ注意事項

⚠️ **重要:**
1. **秘密鍵は絶対に公開しないでください**
2. **秘密鍵はGitにコミットしないでください** (`.gitignore`に`keys/`を追加済み)
3. **本番環境では環境変数またはシークレット管理サービスを使用してください**
4. **秘密鍵のパーミッションは`600`に設定されます**

### 生成後の設定

環境変数で鍵を指定します:

```bash
# .env ファイル
JWT_ALGORITHM=RS256
JWT_PRIVATE_KEY_PATH=keys/jwt_private.pem
JWT_PUBLIC_KEY_PATH=keys/jwt_public.pem

# または、鍵の内容を直接指定
JWT_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n..."
JWT_PUBLIC_KEY="-----BEGIN PUBLIC KEY-----\n..."
```

## 📚 関連ドキュメント

- [JWT RS256移行ガイド](../../docs/jwt_rs256_migration.md)
- [IP制限設定](../../docs/ip_restriction.md)
- [環境変数設定例](../../docs/env_example.md)
