#!/bin/bash
set -e

# Извлекаем публичный ключ из стандартного расположения
PUBLIC_KEY=$(grep 'public key:' ~/.config/sops/age/keys.txt | sed 's/.*public key: //')

if [ -z "$PUBLIC_KEY" ]; then
    echo "❌ Не найден публичный ключ в ~/.config/sops/age/keys.txt"
    echo "   Создайте его: age-keygen -o ~/.config/sops/age/keys.txt"
    exit 1
fi

echo "🔐 Шифрование секретов..."

# --- .env файлы (формат dotenv) ---
echo ""
echo "📄 .env файлы:"
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
        # Проверяем, не зашифрован ли уже
        if head -1 "$env_file" | grep -q "ENC\["; then
            echo "  ⏭️  $env_file (уже зашифрован)"
        else
            echo "  🔒 $env_file"
            sops -e -i --input-type dotenv --age "$PUBLIC_KEY" "$env_file"
        fi
    else
        echo "  ⚠️  $env_file (не найден)"
    fi
done

# --- Сертификаты и ключи (формат binary) ---
echo ""
echo "🔑 Сертификаты alpha_hook/certs/:"
if [ -d "alpha_hook/certs" ]; then
    find alpha_hook/certs -type f \( -name "*.crt" -o -name "*.key" -o -name "*.pem" \) | while read cert_file; do
        # Проверяем, не зашифрован ли уже (бинарный SOPS-файл не является текстом)
        if file "$cert_file" | grep -q "text"; then
            echo "  🔒 $cert_file"
            sops -e --input-type binary --age "$PUBLIC_KEY" --output "$cert_file" "$cert_file"
        else
            echo "  ⏭️  $cert_file (уже зашифрован)"
        fi
    done
else
    echo "  ⚠️  Папка alpha_hook/certs/ не найдена"
fi

echo ""
echo "✅ Шифрование завершено!"
