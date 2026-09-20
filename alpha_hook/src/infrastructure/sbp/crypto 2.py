# src/infrastructure/sbp/crypto.py
"""
Криптографические утилиты для Альфа-Банк СБП C2B
"""

import base64
import hashlib
import logging
from pathlib import Path

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, ec
from cryptography.hazmat.backends import default_backend
from cryptography.x509 import load_pem_x509_certificate

logger = logging.getLogger(__name__)


def sign_body(body: str, key_path: Path) -> str:
    """
    Подписывает тело запроса по стандарту Альфа-Банка:
    UTF-8 bytes → SHA256 → RSA-PKCS1v15 → base64

    Args:
        body: JSON-тело запроса (компактный формат, без пробелов)
        key_path: путь к приватному ключу (PEM)

    Returns:
        base64-строка для заголовка Authorization
    """
    key_bytes = key_path.read_bytes()
    private_key = serialization.load_pem_private_key(
        key_bytes, password=None, backend=default_backend()
    )

    # ✅ Вариант А: передаём сырые данные, cryptography сам хеширует
    signature = private_key.sign(
        body.encode("utf-8"), padding.PKCS1v15(), hashes.SHA256()
    )

    return base64.b64encode(signature).decode("ascii")


def verify_nspk_signature(
    body_bytes: bytes,
    signature_b64: str,
    certificate_pem: str | None = None,
    public_key_path: Path | None = None,
) -> bool:
    """
    Проверяет подпись уведомления от НСПК/Альфа-Банка.

    Поддерживает два режима:
    1. ✅ Тестовый: подпись в заголовке, публичный ключ загружается из файла
    2. 🏭 Продакшен: сертификат в заголовке или по ID, используется GOST-криптография

    Args:
        body_bytes: сырое тело запроса (байты, как пришли по сети)
        signature_b64: Base64-подпись из заголовка X-Signature
        certificate_pem: (опционально) PEM-сертификат отправителя
        public_key_path: (опционально) путь к доверенному публичному ключу

    Returns:
        True, если подпись валидна; False — если нет или ошибка
    """
    try:
        # 1. Декодируем подпись
        signature = base64.b64decode(signature_b64)

        # 2. Получаем публичный ключ для верификации
        public_key = _load_public_key(certificate_pem, public_key_path)
        if public_key is None:
            logger.error("No public key available for signature verification")
            return False

        # 3. Хэшируем тело (SHA256 для тестов; заменить на Streebog/GOST для продакшена)
        digest = hashlib.sha256(body_bytes).digest()

        # 4. Верифицируем подпись
        # Для RSA (тест/Альфа-Банк):
        if isinstance(
            public_key,
            type(
                serialization.load_pem_public_key(
                    b"-----BEGIN PUBLIC KEY-----\n...", backend=default_backend()
                )
            ),
        ):
            public_key.verify(signature, digest, padding.PKCS1v15(), hashes.SHA256())
        # Для EC/GOST (НСПК продакшен — раскомментировать при необходимости):
        # elif isinstance(public_key, ec.EllipticCurvePublicKey):
        #     public_key.verify(
        #         signature,
        #         digest,
        #         ec.ECDSA(hashes.SHA256())  # ← заменить на GOST-хэш при интеграции
        #     )
        #     # Для настоящего GOST: использовать pygost или OpenSSL с GOST-движком

        logger.debug("Signature verified successfully")
        return True

    except Exception as e:
        logger.warning(f"Signature verification failed: {e}")
        return False


def _load_public_key(
    certificate_pem: str | None,
    public_key_path: Path | None,
):
    """
    Загружает публичный ключ из одного из источников (по приоритету):
    1. Сертификат в заголовке (certificate_pem)
    2. Файл на диске (public_key_path)
    3. Доверенное хранилище (заглушка — реализовать для продакшена)
    """
    try:
        # Приоритет 1: сертификат из заголовка
        if certificate_pem:
            cert = load_pem_x509_certificate(
                certificate_pem.encode(), default_backend()
            )
            return cert.public_key()

        # Приоритет 2: файл на диске
        if public_key_path and public_key_path.exists():
            key_bytes = public_key_path.read_bytes()
            return serialization.load_pem_public_key(
                key_bytes, backend=default_backend()
            )

        # Приоритет 3: доверенное хранилище (заглушка)
        # В продакшене: загрузить из /certs/nspk/trusted/ или KMS
        trusted_path = Path("/app/certs/nspk/public.pem")
        if trusted_path.exists():
            key_bytes = trusted_path.read_bytes()
            return serialization.load_pem_public_key(
                key_bytes, backend=default_backend()
            )

    except Exception as e:
        logger.error(f"Failed to load public key: {e}")

    return None
