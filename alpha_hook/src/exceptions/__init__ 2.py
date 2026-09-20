from .webhook import (
    ValidationError,
    DatabaseError,
    ChecksumError,
    WebhookProcessingError,  # ← добавили обратно
)
from .base import BaseWebhookException

__all__ = [
    "BaseWebhookException",
    "ValidationError",
    "DatabaseError",
    "ChecksumError",
    "WebhookProcessingError",  # ← добавили обратно
]