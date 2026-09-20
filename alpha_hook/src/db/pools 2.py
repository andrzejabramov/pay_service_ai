from asyncpg import Pool, create_pool
from src.settings import settings

# Глобальные пулы
write_pool: Pool | None = None
read_pool: Pool | None = None


async def init_pools():
    """Инициализация пулов подключений к PostgreSQL"""
    global write_pool, read_pool

    if write_pool is None:
        write_pool = await create_pool(str(settings.database_write_url))

    if read_pool is None:
        read_pool = await create_pool(str(settings.database_read_url))


async def close_pools():
    """Закрытие пулов подключений"""
    global write_pool, read_pool

    if write_pool:
        await write_pool.close()
        write_pool = None

    if read_pool:
        await read_pool.close()
        read_pool = None


def get_write_pool() -> Pool:
    """Получить пул для записи (мастер)"""
    if write_pool is None:
        raise RuntimeError("Write pool not initialized")
    return write_pool


def get_read_pool() -> Pool:
    """Получить пул для чтения (реплика)"""
    if read_pool is None:
        raise RuntimeError("Read pool not initialized")
    return read_pool