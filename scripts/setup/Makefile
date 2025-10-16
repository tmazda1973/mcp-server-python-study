# セットアップスクリプト用Makefile

.PHONY: help
.DEFAULT_GOAL := help

# --------------------------------------
# Help
# --------------------------------------
help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

# --------------------------------------
# RSA Key Generation
# --------------------------------------
generate-keys: ## Generate RSA key pair (default: 2048 bits)
	@python generate_rsa_keys.py --private-key ../../keys/jwt_private.pem --public-key ../../keys/jwt_public.pem

generate-keys-force: ## Generate RSA key pair (force overwrite)
	@python generate_rsa_keys.py --private-key ../../keys/jwt_private.pem --public-key ../../keys/jwt_public.pem --force

generate-keys-2048: ## Generate RSA key pair (2048 bits)
	@python generate_rsa_keys.py --private-key ../../keys/jwt_private.pem --public-key ../../keys/jwt_public.pem --key-size 2048

generate-keys-4096: ## Generate RSA key pair (4096 bits)
	@python generate_rsa_keys.py --private-key ../../keys/jwt_private.pem --public-key ../../keys/jwt_public.pem --key-size 4096

generate-keys-custom: ## Generate RSA key pair (custom path, usage: make generate-keys-custom PRIVATE=path PUBLIC=path)
	@if [ -z "$(PRIVATE)" ] || [ -z "$(PUBLIC)" ]; then \
		echo "ERROR: PRIVATE と PUBLIC を指定してください"; \
		echo "使用例: make generate-keys-custom PRIVATE=keys/my_private.pem PUBLIC=keys/my_public.pem"; \
		exit 1; \
	fi
	@python generate_rsa_keys.py --private-key $(PRIVATE) --public-key $(PUBLIC)

# --------------------------------------
# Docker環境用
# --------------------------------------
docker-generate-keys: ## Generate RSA key pair in Docker container
	@docker-compose -f ../../docker-compose.yml exec app python scripts/setup/generate_rsa_keys.py

docker-generate-keys-force: ## Generate RSA key pair in Docker container (force overwrite)
	@docker-compose -f ../../docker-compose.yml exec app python scripts/setup/generate_rsa_keys.py --force

