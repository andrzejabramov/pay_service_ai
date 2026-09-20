# alpha_hook/src/routers/webhook.py

"""
Роутер для обработки вебхуков от Альфа-Банка
"""

from fastapi import APIRouter, Depends, Request
from loguru import logger

from src.dependencies.webhook import get_validated_payload
from src.services.db_service import save_webhook_result  # ← заменили имя функции
from src.middleware.request_id import request_id_ctx
from src.db.pools import get_write_pool
from src.schemas.webhook import AlfaBankCallback, ApiResponse

router = APIRouter(tags=["Alfa Bank SBP Webhooks"])


@router.post("/callback", response_model=ApiResponse)
async def handle_webhook(
    request: Request,
    payload: AlfaBankCallback | None = Depends(get_validated_payload)
):
    """
    Обработка вебхука от Альфа-Банка.
    """
    request_id = request_id_ctx.get()

    # Логируем входящий запрос
    body = await request.body()
    raw_body = body.decode('utf-8', errors='ignore')
    content_type = request.headers.get("content-type", "")

    logger.info(
        "📥 Incoming webhook",
        extra={
            "request_id": request_id,
            "content_type": content_type,
            "body_length": len(raw_body),
            "is_valid": payload is not None,
            "layer": "router"
        }
    )

    # Обрабатываем через сервисный слой
    pool = get_write_pool()
    result = await save_webhook_result(  # ← заменили имя функции
        pool=pool,
        raw_body=raw_body,
        content_type=content_type,
        validated_payload=payload,
        request_id=request_id
    )

    # Всегда возвращаем 200 OK
    return ApiResponse(
        status="ok",
        message="Callback accepted",
        request_id=request_id
    )


@router.get("/test", response_model=ApiResponse)
async def test_endpoint():
    """Тестовый эндпоинт для проверки доступности сервиса"""
    request_id = request_id_ctx.get()
    logger.info("🧪 Test endpoint called", extra={"request_id": request_id, "layer": "router"})
    return ApiResponse(
        status="ok",
        message="Alfa Hook service is running",
        request_id=request_id
    )