# alpha_hook/src/logger_config.py
"""
Настройка логирования
"""

from loguru import logger
import sys
from pathlib import Path


def setup_logger():
    """Настройка логгера с ротацией"""

    # Удаляем стандартный handler
    logger.remove()

    # Формат для консоли (цветной, читаемый)
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
               "<level>{level: <8}</level> | "
               "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
               "<level>{message}</level>",
        level="INFO",
        colorize=True
    )

    # Формат для файла (JSON, для анализа)
    logger.add(
        "logs/alpha_hook_{time:YYYY-MM-DD}.log",
        rotation="00:00",
        retention="30 days",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {name} | {message}",
        level="DEBUG",
        serialize=True  # JSON формат для машинного анализа
    )

    # Отдельный файл только для ошибок
    logger.add(
        "logs/alpha_hook_errors_{time:YYYY-MM-DD}.log",
        rotation="00:00",
        retention="90 days",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {name} | {message}",
        level="ERROR",
        serialize=True
    )

    return logger