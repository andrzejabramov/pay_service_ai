# tests/test_webhook.py

import pytest
from httpx import AsyncClient
from typing import Dict, Any
from unittest.mock import AsyncMock, patch

# Импортируем модуль pools для подмены
from alpha_hook.src.db import pools


@pytest.mark.asyncio
async def test_valid_webhook(client: AsyncClient, valid_payload: Dict[str, Any]):
    """Тест валидного webhook"""
    
    # Создаем мок-пул прямо в тесте
    mock_pool = AsyncMock()
    mock_conn = AsyncMock()
    mock_conn.fetchval.return_value = {"ans": "ok", "id": "test-uuid"}
    mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
    
    # Сохраняем оригинальную функцию
    original_get_write_pool = pools.get_write_pool
    
    # Подменяем функцию
    async def mock_get_write_pool():
        return mock_pool
    pools.get_write_pool = mock_get_write_pool
    
    try:
        response = await client.post(
            "/webhook/callback",
            json=valid_payload
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "request_id" in data
    finally:
        # Восстанавливаем оригинал
        pools.get_write_pool = original_get_write_pool


@pytest.mark.asyncio
async def test_invalid_webhook(client: AsyncClient, invalid_payload: Dict[str, Any]):
    """Тест невалидного webhook"""
    
    # Создаем мок-пул прямо в тесте
    mock_pool = AsyncMock()
    mock_conn = AsyncMock()
    mock_conn.fetchval.return_value = {"ans": "ok", "id": "test-uuid"}
    mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
    
    # Сохраняем оригинальную функцию
    original_get_write_pool = pools.get_write_pool
    
    # Подменяем функцию
    async def mock_get_write_pool():
        return mock_pool
    pools.get_write_pool = mock_get_write_pool
    
    try:
        response = await client.post(
            "/webhook/callback",
            json=invalid_payload
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "request_id" in data
    finally:
        # Восстанавливаем оригинал
        pools.get_write_pool = original_get_write_pool