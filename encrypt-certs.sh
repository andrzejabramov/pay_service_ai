#!/bin/bash
set -e

# Правильно извлекаем публичный ключ (всё после "public key: ")
PUBLIC_KEY=$(grep 'public key:' ~/.config/sops/age/keys.txt | sed 's/.*public key: //')

if [ -z "$PUBLIC_KEY" ]; then
    echo "❌ Не найден публичный ключ в ~/.config/sops/age/keys.txt"
    exit 1
fi

echo "🔐 Шифрую сертификаты и ключи..."
echo "Публичный ключ: $PUBLIC_KEY"

find alpha_hook/certs -type f \( -name "*.crt" -o -name "*.key" -o -name "*.pem" \) | while read cert_file; do
    echo "  - $cert_file"
    sops -e --input-type binary --age "$PUBLIC_KEY" --output "$cert_file" "$cert_file"
done

echo "✅ Шифрование завершено!"
