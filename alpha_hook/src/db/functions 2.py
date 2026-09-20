# alpha_hook/src/db/functions.py
from asyncpg import Connection
from typing import Any, Dict
import json  # ← ИМПОРТИРУЕМ json!


async def call_webhook_function(conn: Connection, payload: Dict[str, Any]) -> Any:
    """
    Вызов хранимой процедуры alpha_hook.log_callback().

    Строго по шаблону webhook_2can:
    1. dict → json.dumps() → JSON-строка
    2. Передаём строку с ::json cast
    """
    # Сериализуем dict → JSON-строку
    json_str = json.dumps(payload, ensure_ascii=False)

    # Вызываем функцию с явным cast ::json
    result = await conn.fetchval(
        "SELECT alpha_hook.log_callback($1::json)",  # ← имя функции + тип аргумента
        json_str  # ← JSON-строка, НЕ dict!
    )
    return result