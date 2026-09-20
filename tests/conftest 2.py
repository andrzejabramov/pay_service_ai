# tests/conftest.py

import pytest
import sys
from pathlib import Path
from typing import AsyncGenerator, Dict, Any
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock

# Добавляем путь к alpha_hook
alpha_hook_path = Path(__file__).parent.parent / "alpha_hook"
sys.path.insert(0, str(alpha_hook_path))

# Импортируем модуль pools напрямую из файла
from alpha_hook.src.db import pools


@pytest.fixture(autouse=True)
def mock_db_pools():
    """Принудительно подменяем функцию get_write_pool"""

    # Создаем мок-пул
    mock_pool = AsyncMock()
    mock_conn = AsyncMock()
    mock_conn.fetchval.return_value = {"ans": "ok", "id": "test-uuid"}
    mock_conn.fetch.return_value = []
    mock_conn.execute.return_value = "INSERT 0 1"
    mock_pool.acquire.return_value.__aenter__.return_value = mock_conn

    # Прямая замена функции в модуле
    async def mock_get_write_pool():
        return mock_pool

    # Сохраняем оригинальную функцию
    original_get_write_pool = pools.get_write_pool

    # Подменяем
    pools.get_write_pool = mock_get_write_pool

    yield

    # Восстанавливаем оригинал
    pools.get_write_pool = original_get_write_pool


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Фикстура HTTP-клиента"""
    from alpha_hook.src.main import app

    async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
    ) as client:
        yield client


@pytest.fixture
def valid_payload() -> Dict[str, Any]:
    """Валидный payload"""
    return {
        "orderNumber": "DRV_TEST_001",
        "mdOrder": "3ff6962a-7dcc-4283-ab50-a6d7dd3386fe",
        "operation": "deposited",
        "status": 1,
        "amount": 150000,
        "checksum": "TEST"
    }


@pytest.fixture
def invalid_payload() -> Dict[str, Any]:
    """Невалидный payload"""
    return {
        "some": "field",
        "another": "value"
    }