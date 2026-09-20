"""
Базовые исключения приложения
"""


class BaseWebhookException(Exception):
    """Базовый класс для всех исключений вебхуков"""

    def __init__(self, message: str, details: dict = None):
        self.message = message
        self.details = details or {}
        super().__init__(message)