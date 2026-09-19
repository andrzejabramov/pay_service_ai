#!/bin/bash
set -e

PUBLIC_KEY=$(grep 'public key:' ~/.config/sops/age/keys.txt | sed 's/.*public key: //')

if [ -z "$PUBLIC_KEY" ]; then
    echo "❌ Не найден публичный ключ"
    exit 1
fi

echo "🔐 Шифрую .env файлы..."
echo "Публичный ключ: $PUBLIC_KEY"

ENV_FILES=(
    ".env"
    "alpha_hook/.env"
    "auth/.env"
    "contracts/.env"
    "payment_reply/.env"
    "users/.env"
    "webhook_2can/.env"
)

for env_file in "${ENV_FILES[@]}"; do
    if [ -f "$env_file" ]; then
        echo "  - $env_file"
        sops -e -i --input-type dotenv --age "$PUBLIC_KEY" "$env_file"
    else
        echo "  ⚠️  Файл не найден: $env_file"
    fi
done

echo "✅ Готово!"
