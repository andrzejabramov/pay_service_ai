# alpha_hook/src/utils/security.py
"""
Утилиты для проверки безопасности вебхуков
"""

import hmac
import hashlib
from typing import Dict
from loguru import logger
from src.middleware.request_id import request_id_ctx
from src.settings import settings


def verify_alfa_checksum(
        params: Dict[str, str],
        received_checksum: str
) -> bool:
    """
    Проверка контрольной суммы по алгоритму Альфа-Банка.

    Args:
        params: словарь параметров из запроса
        received_checksum: контрольная сумма из параметра checksum

    Returns:
        bool: True если контрольные суммы совпадают
    """
    request_id = request_id_ctx.get()

    if not received_checksum:
        logger.warning("Empty checksum received", extra={"request_id": request_id})
        return False

    # Получаем секретный ключ из настроек
    secret_key = settings.ALFA_SECRET_KEY
    if not secret_key:
        logger.error("ALFA_SECRET_KEY not configured", extra={"request_id": request_id})
        return False

    # 1. Удаляем checksum и sign_alias (если есть)
    filtered = {
        k: v for k, v in params.items()
        if k not in ('checksum', 'sign_alias')
    }

    # 2. Сортируем по ключам
    sorted_items = sorted(filtered.items(), key=lambda x: x[0])

    # 3. Формируем строку "key1;value1;key2;value2;...;"
    signature_string = ";".join(f"{k};{v}" for k, v in sorted_items) + ";"

    # 4. Вычисляем HMAC-SHA256
    expected = hmac.new(
        key=secret_key.encode('utf-8'),
        msg=signature_string.encode('utf-8'),
        digestmod=hashlib.sha256
    ).hexdigest().upper()

    # 5. Сравниваем
    is_valid = hmac.compare_digest(expected, received_checksum.upper())

    if is_valid:
        logger.info("✅ Checksum verification passed", extra={"request_id": request_id})
    else:
        logger.warning(
            "❌ Checksum verification failed",
            extra={
                "request_id": request_id,
                "expected": expected[:16] + "...",
                "received": received_checksum[:16] + "..."
            }
        )

    return is_valid


def generate_test_checksum(
        params: Dict[str, str],
        secret_key: str
) -> str:
    """
    Генерирует контрольную сумму для тестовых целей.
    """
    filtered = {
        k: v for k, v in params.items()
        if k not in ('checksum', 'sign_alias')
    }
    sorted_items = sorted(filtered.items(), key=lambda x: x[0])
    signature_string = ";".join(f"{k};{v}" for k, v in sorted_items) + ";"

    return hmac.new(
        key=secret_key.encode('utf-8'),
        msg=signature_string.encode('utf-8'),
        digestmod=hashlib.sha256
    ).hexdigest().upper()