#!/bin/bash
set -e
cd "$(dirname "$0")"

export SOPS_AGE_KEY_FILE="${HOME}/.config/sops/age/keys.txt"

while IFS= read -r -d '' file; do
    while IFS='=' read -r key value; do
        [[ -z "$key" || "$key" =~ ^# ]] && continue
        export "$key=$value"
    done < <(sops -d --input-type dotenv --output-type dotenv "$file" 2>/dev/null)
done < <(find . -name ".env.sops" -not -path "*/.venv/*" -not -path "*/.git/*" -print0)

# Отладка: показываем, что реально попало в окружение

docker compose "$@"
