📋 ДАЙДЖЕСТ ПРОЕКТА: Безопасность секретов с SOPS

## 🎯 Контекст проекта

**Проект**: Монорепозиторий интернет-магазина `pay_servises_ai`  
**Стек**: FastAPI (Python), PostgreSQL (с хранимыми процедурами), Redis, RabbitMQ, Docker Compose v2  
**ОС**: macOS M1 (разработка), Ubuntu VM (продакшен)  
**Сервисы**: `alpha_hook/`, `auth/`, `contracts/`, `payment_reply/`, `users/`, `webhook_2can/`, `frontend/`  
**Особенности**:

- Микросервисная архитектура
- Интеграция с Альфа-Банком (mTLS сертификаты в `alpha_hook/certs/`)
- Внешние API: OpenRouter, 2can, почтовые/СМС сервисы, онлайн-касса
- Принцип "Single Source of Truth" для конфигураций

---

## 🔒 Проблема безопасности

**Угроза**: AI-агент (Cursor, Claude Code и т.д.) имеет доступ к файловой системе и может прочитать `.env` файлы с реальными секретами (пароли БД, API-ключи, сертификаты).

**Требования к решению**:

1. ✅ Агент НЕ должен иметь возможности прочитать секреты
2. ✅ Тесты должны работать с РЕАЛЬНЫМИ секретами (не фейковыми)
3. ✅ Решение должно работать локально (с агентом) и на продакшене (без агента)
4. ✅ Сохранить принцип "единого источника истины" (без дублирования конфигураций)
5. ✅ Удобная миграция между окружениями
6. ✅ Секреты НЕ должны записываться на диск в открытом виде (даже временно!)

---

## 🔍 Рассмотренные решения

### Метод 1: OS Permissions (ограничение прав на уровне ОС)

- Файл `.env` принадлежит `root`, права `600`
- Запуск через `sudo docker compose`
- **Плюсы**: Просто, надежно
- **Минусы**: При компрометации сервера — все секреты сразу

### Метод 2: Ephemeral Secrets (менеджер паролей)

- Секреты в 1Password/Bitwarden, на диске нет
- `op run --env-file=".env.example" -- docker compose up`
- **Плюсы**: Золотой стандарт, аудит доступа
- **Минусы**: Зависимость от внешнего сервиса

### Метод 3: SOPS (прозрачное шифрование) ✅ ВЫБРАН

- Файлы шифруются в Git, ключ расшифровки локально
- `sops exec-env .env "docker compose up"`
- **Плюсы**: Git-friendly, один файл-источник, миграция тривиальна, индустриальный стандарт
- **Минусы**: Требует установки SOPS

---

## 🛠 Реализация SOPS

### Установка на macOS M1

```bash
brew install sops age
```

### Генерация ключа

```bash
mkdir -p ~/.config/sops/age
age-keygen -o ~/.config/sops/age/keys.txt
chmod 600 ~/.config/sops/age/keys.txt

# Получить публичный ключ
grep 'public key:' ~/.config/sops/age/keys.txt | sed 's/.*public key: //'
# age1xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### Конфигурация `.sops.yaml` (в корне проекта)

```yaml
creation_rules:
  # Все .env файлы (формат dotenv)
  - path_regex: \.env$
    age: age1xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

  # Сертификаты (формат binary)
  - path_regex: ^alpha_hook/certs/.*\.(crt|key|pem)$
    age: age1xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### Шифрование файлов

**Для .env файлов (dotenv формат)**:

```bash
PUBLIC_KEY=$(grep 'public key:' ~/.config/sops/age/keys.txt | sed 's/.*public key: //')

sops -e -i --input-type dotenv --age "$PUBLIC_KEY" .env
sops -e -i --input-type dotenv --age "$PUBLIC_KEY" alpha_hook/.env
# ... и т.д. для всех сервисов
```

**Для сертификатов (binary формат)**:

```bash
sops -e --input-type binary --age "$PUBLIC_KEY" --output alpha_hook/certs/mtls/client.crt alpha_hook/certs/mtls/client.crt
# ... и т.д. для всех .crt, .key, .pem
```

### Скрипты автоматизации

**`scripts/encrypt-all.sh`** — массовое шифрование:

```bash
#!/bin/bash
set -e

PUBLIC_KEY=$(grep 'public key:' ~/.config/sops/age/keys.txt | sed 's/.*public key: //')

echo "🔐 Шифрование секретов..."

# .env файлы
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
    fi
done

# Сертификаты
echo "🔑 Шифрую сертификаты..."
find alpha_hook/certs -type f \( -name "*.crt" -o -name "*.key" -o -name "*.pem" \) | while read cert_file; do
    echo "  - $cert_file"
    sops -e --input-type binary --age "$PUBLIC_KEY" --output "$cert_file" "$cert_file"
done

echo "✅ Готово!"
```

---

## 🐛 Решённые проблемы

### Проблема 1: SOPS не шифрует .env файлы

**Симптом**: `config file not found, or has no creation rules`  
**Причина**: Не указан ключ явно  
**Решение**: Использовать `--age "$PUBLIC_KEY"` вместо зависимости от `.sops.yaml`

### Проблема 2: SOPS не шифрует PEM-файлы

**Симптом**: Файлы остаются в открытом виде  
**Причина**: SOPS по умолчанию ожидает YAML/JSON  
**Решение**: Использовать `--input-type binary` для сертификатов

### Проблема 3: Docker Compose не работает с зашифрованными .env

**Симптом**: `invalid IP address: ENC[AES256_GCM...]`  
**Причина**: Docker автоматически читает `.env` при любом вызове  
**Решение**: Использовать process substitution для расшифровки в память:

```bash
docker compose --env-file <(sops -d --input-type dotenv .env.sops) up -d
```

### Проблема 4: Git игнорирует зашифрованные файлы

**Симптом**: `git status` не показывает `.env` файлы  
**Причина**: Локальные `.gitignore` в папках сервисов  
**Решение**: Удалить правила `.env` из `alpha_hook/.gitignore`, `users/.gitignore` и т.д.:

```bash
sed -i '' '/^\.env$/d' alpha_hook/.gitignore
```

---

## ✅ Текущий статус

**Сделано**:

- ✅ Установлены SOPS и age на macOS
- ✅ Сгенерирован ключ age
- ✅ Создан `.sops.yaml` с правилами шифрования
- ✅ Зашифрованы все `.env` файлы (формат dotenv)
- ✅ Зашифрованы все сертификаты в `alpha_hook/certs/` (формат binary)
- ✅ Созданы скрипты автоматизации в `scripts/`
- ✅ Обновлён `.gitignore` (разрешены зашифрованные файлы)
- ✅ Файлы добавлены в Git

**Проблема на момент прерывания**:

- ❌ Docker Compose не может работать с зашифрованными `.env` файлами
- ❌ Нужно реализовать процесс расшифровки в память (без записи на диск)

---

## 🎯 Следующие шаги (для нового чата)

1. **Реализовать правильную интеграцию Docker Compose + SOPS**:
   - Использовать process substitution `<(sops -d ...)` для расшифровки в память
   - Создать скрипты `dev-start.sh`, `dev-logs.sh`, `dev-stop.sh`
   - Убедиться, что расшифрованные файлы НЕ записываются на диск

2. **Решить проблему сервисных `.env.sops`**:
   - Вариант A: Перенести все переменные в корневой `.env.sops` с префиксами
   - Вариант B: Использовать `environment` в `docker-compose.yml` с подстановкой

3. **Протестировать полный workflow**:
   - Запуск проекта: `./scripts/dev-start.sh up -d`
   - Просмотр логов: `./scripts/dev-logs.sh --tail=30`
   - Остановка: `./scripts/dev-stop.sh`

4. **Настроить деплой на Ubuntu VM**:
   - Установить SOPS на сервер
   - Передать приватный ключ (`scp` или через менеджер паролей)
   - Настроить CI/CD пайплайн

5. **Дополнительные улучшения**:
   - Настроить `.cursorignore` для IDE
   - Добавить ротацию ключей
   - Настроить мониторинг доступа к секретам

---

## 📁 Структура проекта (финальная)

```
pay_servises_ai/
├── .sops.yaml                    # Правила SOPS (публичный ключ) ✅ коммитить
├── .env.sops                     # Зашифрованный корневой .env ✅ коммитить
├── .gitignore                    # Разрешает .env.sops, запрещает .env
├── scripts/
│   ├── encrypt-all.sh            # Скрипт шифрования ✅ коммитить
│   ├── dev-start.sh              # Запуск с расшифровкой в память ✅ коммитить
│   ├── dev-logs.sh               # Просмотр логов ✅ коммитить
│   └── dev-stop.sh               # Остановка ✅ коммитить
├── alpha_hook/
│   ├── .env.sops                 # Зашифрован ✅ коммитить
│   └── certs/
│       ├── ca/*.crt              # Зашифрованы ✅ коммитить
│       ├── mtls/*.crt, *.key     # Зашифрованы ✅ коммитить
│       └── signing/*.crt, *.key  # Зашифрованы ✅ коммитить
├── auth/.env.sops                # Зашифрован ✅ коммитить
├── users/.env.sops               # Зашифрован ✅ коммитить
└── ...

НЕ коммитить:
~/.config/sops/age/keys.txt       # Приватный ключ ❌ НИКОГДА
```

---

## 🔑 Ключевые принципы

1. **Секреты никогда не записываются на диск в открытом виде** — только в оперативную память через process substitution
2. **Публичный ключ age** — не секрет, коммитится в `.sops.yaml`
3. **Приватный ключ** — хранится только локально в `~/.config/sops/age/keys.txt` с правами `600`
4. **Зашифрованные файлы** — безопасны для Git, коммитятся
5. **Расшифрованные файлы** — существуют только в памяти во время выполнения команды

---
