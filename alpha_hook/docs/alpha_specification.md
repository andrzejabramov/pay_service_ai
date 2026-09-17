~/Desktop/Urban/pay_services/
│
├── 📄 docker-compose.yml                 # Главный оркестратор всех сервисов
├── 📄 .env                                # Общие переменные окружения (НЕ В GIT!)
├── 📄 .gitignore                          # Исключения для гита
├── 📄 README.md                            # Описание проекта
│
├── 📁 helpers/                             # 🔧 Вспомогательные скрипты (НЕ для продакшена)
│   ├── 📄 README.md
│   ├── 📄 check_imports.py                 # Скрипт проверки импортов
│   ├── 📄 generate_env_template.py         # Генерация .env.example из структуры
│   ├── 📁 docker/
│   │   ├── 📄 cleanup.sh                    # Очистка Docker-образов и волюмов
│   │   └── 📄 build_all.sh                   # Сборка всех сервисов
│   └── 📁 logs/
│       └── 📄 parse_alpha_hook_logs.py       # Анализ логов alpha_hook
│
├── 📁 postgres/                             # Конфигурация PostgreSQL (мастер/реплика)
│   ├── 📁 master/
│   │   ├── 📄 postgresql.conf
│   │   ├── 📄 pg_hba.conf
│   │   └── 📄 init-master.sh
│   └── 📁 replica/
│       ├── 📄 postgresql.conf
│       └── 📄 init-replica.sh
│
├── 📁 sql/                                   # SQL-схемы и миграции (ручные)
│   ├── 📁 schemas/
│   │   ├── 📁 auth/                           # Схема для сервиса auth
│   │   │   ├── 📁 tables/
│   │   │   └── 📁 functions/
│   │   ├── 📁 accounts/                        # Схема для сервиса users (accounts)
│   │   │   ├── 📁 tables/
│   │   │   │   ├── 📄 users.sql
│   │   │   │   ├── 📄 user_contacts.sql
│   │   │   │   └── 📄 user_groups.sql
│   │   │   └── 📁 functions/
│   │   │       ├── 📄 create_user.sql
│   │   │       ├── 📄 get_user_by_id.sql
│   │   │       └── 📄 ... (остальные функции)
│   │   ├── 📁 to_can/                          # Схема для webhook_2can
│   │   │   ├── 📁 tables/
│   │   │   │   ├── 📄 syspay.sql
│   │   │   │   └── 📄 merchant_tap2go.sql
│   │   │   └── 📁 functions/
│   │   │       ├── 📄 f_syspay.sql
│   │   │       └── 📄 f_payment.sql
│   │   └── 📁 alpha_hook/                      # 🆕 Схема для alpha_hook
│   │       ├── 📁 tables/
│   │       │   └── 📄 01_create_logs_table.sql   # Таблица logs (id_uuid, payload jsonb, status enum)
│   │       └── 📁 functions/
│   │           └── 📄 01_log_callback.sql        # Функция alpha_hook.log_callback
│   └── 📁 migrations/                           # Ручные миграции для всех схем
│       ├── 📄 2026_03_06_create_core_schema.sql     # Создание схемы core
│       └── 📄 2026_03_06_create_user_identities.sql # Таблица core.user_identities
│
├── 📁 auth/                                    # Сервис аутентификации
│   ├── 📄 Dockerfile
│   ├── 📄 requirements.txt
│   ├── 📄 .env                                 # Специфичные для сервиса переменные (опционально)
│   ├── 📁 src/
│   │   ├── 📄 __init__.py
│   │   ├── 📄 main.py
│   │   ├── 📄 settings.py
│   │   ├── 📁 api/
│   │   │   └── 📁 v1/
│   │   │       ├── 📄 __init__.py
│   │   │       └── 📄 routes.py
│   │   ├── 📁 core/
│   │   │   └── 📄 config.py
│   │   ├── 📁 db/
│   │   │   ├── 📄 __init__.py
│   │   │   ├── 📄 pool.py
│   │   │   └── 📄 functions.py
│   │   ├── 📁 schemas/
│   │   │   └── 📄 auth.py
│   │   ├── 📁 services/
│   │   │   └── 📄 auth_service.py
│   │   └── 📁 utils/
│   │       └── 📄 security.py
│   └── 📁 logs/
│
├── 📁 users/                                   # Сервис управления пользователями
│   ├── 📄 Dockerfile
│   ├── 📄 requirements.txt
│   ├── 📄 .env
│   ├── 📁 src/
│   │   ├── 📄 __init__.py
│   │   ├── 📄 main.py
│   │   ├── 📄 settings.py
│   │   ├── 📁 core/
│   │   ├── 📁 db/
│   │   │   ├── 📄 __init__.py
│   │   │   ├── 📄 pools.py
│   │   │   └── 📄 functions.py
│   │   ├── 📁 routers/
│   │   │   └── 📁 accounts/
│   │   │       ├── 📄 users.py
│   │   │       ├── 📄 user_contacts.py
│   │   │       └── 📄 user_groups.py
│   │   ├── 📁 schemas/
│   │   │   └── 📄 users.py
│   │   ├── 📁 services/
│   │   │   └── 📄 users.py
│   │   └── 📁 utils/
│   │       ├── 📄 __init__.py
│   │       └── 📄 json_utils.py
│   └── 📁 logs/
│
├── 📁 webhook_2can/                           # Существующий сервис вебхуков
│   ├── 📄 Dockerfile
│   ├── 📄 requirements.txt
│   ├── 📄 .env
│   ├── 📁 src/
│   │   ├── 📄 __init__.py
│   │   ├── 📄 main.py
│   │   ├── 📄 settings.py
│   │   ├── 📁 db/
│   │   │   ├── 📄 __init__.py
│   │   │   ├── 📄 pools.py
│   │   │   └── 📄 functions.py
│   │   ├── 📁 routers/
│   │   │   └── 📄 webhook.py
│   │   ├── 📁 schemas/
│   │   │   └── 📄 webhook.py
│   │   ├── 📁 services/
│   │   │   └── 📄 db_service.py
│   │   └── 📁 utils/
│   └── 📁 logs/
│
└── 📁 alpha_hook/                             # 🆕 Наш новый сервис (ГОТОВО!)
    ├── 📄 Dockerfile
    ├── 📄 requirements.txt
    ├── 📄 .env                                 # Специфичные переменные (опционально)
    ├── 📁 src/
    │   ├── 📄 __init__.py
    │   ├── 📄 main.py                          # FastAPI app с lifespan и middleware
    │   ├── 📄 settings.py                      # Настройки (extra="ignore", секреты без default)
    │   ├── 📄 logger_config.py                  # Настройка loguru (JSON + ротация)
    │   ├── 📁 core/
    │   │   ├── 📄 __init__.py
    │   │   └── 📄 handlers.py                    # Глобальные exception handlers (всегда 200 OK)
    │   ├── 📁 db/
    │   │   ├── 📄 __init__.py
    │   │   ├── 📄 pools.py                       # write_pool / read_pool
    │   │   └── 📄 functions.py                    # call_webhook_function (вызов log_callback)
    │   ├── 📁 dependencies/
    │   │   ├── 📄 __init__.py
    │   │   ├── 📄 db.py                           # get_db_pool
    │   │   └── 📄 webhook.py                      # process_webhook_payload (с логированием)
    │   ├── 📁 exceptions/
    │   │   ├── 📄 __init__.py
    │   │   ├── 📄 base.py
    │   │   └── 📄 webhook.py                       # Кастомные исключения
    │   ├── 📁 middleware/
    │   │   ├── 📄 __init__.py
    │   │   ├── 📄 request_id.py                    # Корреляция логов (с token reset)
    │   │   └── 📄 logging.py                       # Мидлварь для логирования запросов
    │   ├── 📁 routers/
    │   │   ├── 📄 __init__.py
    │   │   └── 📄 webhook.py                       # POST /callback и GET /test
    │   ├── 📁 schemas/
    │   │   ├── 📄 __init__.py
    │   │   └── 📄 webhook.py                       # WebhookPayload (валидация полей)
    │   ├── 📁 services/
    │   │   ├── 📄 __init__.py
    │   │   └── 📄 db_service.py                    # call_webhook_function (с retry и ошибками)
    │   └── 📁 utils/
    │       ├── 📄 __init__.py
    │       ├── 📄 logger.py
    │       └── 📄 security.py                       # verify_alfa_callback_signature (пока заглушка)
    └── 📁 logs/                                     # Логи, проброшенные на хост
        └── 📄 alpha_hook_2026-03-06.log

alpha_hook/src/
├── routers/
│   └── webhook.py           ← Роутер (точка входа)
├── dependencies/
│   ├── db.py                 ← Получение пула БД
│   └── webhook.py            ← Валидация payload
├── services/
│   └── db_service.py         ← Вызов хранимой процедуры
├── exceptions/
│   ├── __init__.py
│   ├── base.py               ← Базовые исключения
│   └── webhook.py            ← Специфичные исключения
├── db/
│   └── pools.py              ← Пулы подключений
└── logger_config.py          ← Настройка логирования



