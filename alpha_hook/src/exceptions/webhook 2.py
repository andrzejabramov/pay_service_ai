"""
Специфичные исключения для вебхуков
"""

from loguru import logger
from src.middleware.request_id import request_id_ctx
from .base import BaseWebhookException


class ValidationError(BaseWebhookException):
    """Ошибка валидации данных"""

    def __init__(self, message: str, details: dict = None):
        request_id = request_id_ctx.get()

        logger.warning(
            "⚠️ VALIDATION ERROR",
            extra={
                "request_id": request_id,
                "error_message": message,
                "error_details": details,
                "exception": self.__class__.__name__,
                "layer": "exceptions"
            }
        )
        super().__init__(message, details)


class DatabaseError(BaseWebhookException):
    """Ошибка при работе с БД"""

    def __init__(self, message: str, details: dict = None):
        request_id = request_id_ctx.get()

        logger.error(
            "❌ DATABASE ERROR",
            extra={
                "request_id": request_id,
                "error_message": message,
                "error_details": details,
                "exception": self.__class__.__name__,
                "layer": "exceptions"
            }
        )
        super().__init__(message, details)


class ChecksumError(BaseWebhookException):
    """Ошибка проверки контрольной суммы"""

    def __init__(self, message: str, details: dict = None):
        request_id = request_id_ctx.get()

        logger.warning(
            "🔐 CHECKSUM ERROR",
            extra={
                "request_id": request_id,
                "error_message": message,
                "error_details": details,
                "exception": self.__class__.__name__,
                "layer": "exceptions"
            }
        )
        super().__init__(message, details)


# Добавь этот класс после остальных
class WebhookProcessingError(BaseWebhookException):
    """Ошибка при обработке вебхука"""

    def __init__(self, message: str, details: dict = None):
        request_id = request_id_ctx.get()

        logger.error(
            "❌ WEBHOOK PROCESSING ERROR",
            extra={
                "request_id": request_id,
                "error_message": message,
                "error_details": details,
                "exception": self.__class__.__name__,
                "layer": "exceptions"
            }
        )
        super().__init__(message, details)


# Добавь этот класс после остальных
class WebhookProcessingError(BaseWebhookException):
    """Ошибка при обработке вебхука (общая)"""

    def __init__(self, message: str, details: dict = None):
        request_id = request_id_ctx.get()

        logger.error(
            "❌ WEBHOOK PROCESSING ERROR",
            extra={
                "request_id": request_id,
                "error_message": message,
                "error_details": details,
                "exception": self.__class__.__name__,
                "layer": "exceptions"
            }
        )
        super().__init__(message, details)