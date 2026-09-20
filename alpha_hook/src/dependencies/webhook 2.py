# alpha_hook/src/dependencies/webhook.py

from fastapi import Depends, Request
from loguru import logger
from typing import Optional

from src.schemas.webhook import AlfaBankCallback
from src.middleware.request_id import request_id_ctx
from src.utils.security import verify_alfa_checksum  # ← убрали TEST_SECRET_KEY
from src.settings import settings


async def get_validated_payload(request: Request) -> Optional[AlfaBankCallback]:
    """
    Dependency: парсит и валидирует входящий payload.
    """
    request_id = request_id_ctx.get()
    content_type = request.headers.get("content-type", "")

    logger.debug(
        "🔍 Starting payload validation",
        extra={
            "request_id": request_id,
            "content_type": content_type,
            "layer": "dependencies"
        }
    )

    try:
        form = await request.form()
        params = dict(form)

        if "status" in params and isinstance(params["status"], str):
            params["status"] = int(params["status"])

        # Проверяем контрольную сумму
        secret_key = settings.ALFA_SECRET_KEY or "test_secret_key"  # ← теперь берем из settings

        if not verify_alfa_checksum(params, params.get("checksum", ""), secret_key):
            logger.warning(
                "⚠️ Checksum verification failed",
                extra={
                    "request_id": request_id,
                    "orderNumber": params.get("orderNumber"),
                    "mdOrder": params.get("mdOrder")
                }
            )

        payload = AlfaBankCallback(**params)

        logger.info(
            "✅ Payload validation successful",
            extra={
                "request_id": request_id,
                "orderNumber": payload.orderNumber,
                "mdOrder": payload.mdOrder,
                "operation": payload.operation,
                "status": payload.status,
                "layer": "dependencies"
            }
        )

        return payload

    except Exception as e:
        logger.warning(
            "❌ Payload validation failed",
            extra={
                "request_id": request_id,
                "error": str(e),
                "error_type": type(e).__name__,
                "layer": "dependencies"
            }
        )
        return None