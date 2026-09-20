"""
Зависимости для работы с БД
"""

from fastapi import Depends
from loguru import logger
from asyncpg import Pool

from src.db.pools import get_write_pool
from src.middleware.request_id import request_id_ctx


async def get_db_pool() -> Pool:
    """
    Dependency: возвращает пул для записи в БД.
    """
    request_id = request_id_ctx.get()

    logger.debug(
        "🔌 ACQUIRING DB POOL",
        extra={
            "request_id": request_id,
            "layer": "dependencies"
        }
    )

    try:
        pool = get_write_pool()

        logger.debug(
            "✅ DB POOL ACQUIRED",
            extra={
                "request_id": request_id,
                "pool_stats": {
                    "max_size": pool._maxsize if hasattr(pool, '_maxsize') else 'unknown',
                },
                "layer": "dependencies"
            }
        )

        return pool

    except Exception as e:
        logger.error(
            "❌ FAILED TO ACQUIRE DB POOL",
            extra={
                "request_id": request_id,
                "error": str(e),
                "error_type": type(e).__name__,
                "layer": "dependencies"
            }
        )
        raise