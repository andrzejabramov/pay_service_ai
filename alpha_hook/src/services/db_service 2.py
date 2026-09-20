# alpha_hook/src/services/db_service.py

"""
Сервис для работы с БД
"""

from loguru import logger
from asyncpg import Pool, PostgresError
import json
import uuid

from src.schemas.webhook import AlfaBankCallback  # ← заменили WebhookPayload на AlfaBankCallback
from src.exceptions.webhook import DatabaseError, ValidationError
from src.middleware.request_id import request_id_ctx


async def save_webhook_result(
        pool: Pool,
        raw_body: str,
        content_type: str,
        validated_payload: AlfaBankCallback | None,  # ← заменили тип
        request_id: str
) -> dict:
    """
    Сохраняет результат обработки вебхука в БД.
    """
    logger.info(
        "💾 SAVING WEBHOOK TO DATABASE",
        extra={
            "request_id": request_id,
            "is_valid": validated_payload is not None,
            "raw_size": len(raw_body),
            "layer": "service"
        }
    )

    try:
        async with pool.acquire() as conn:
            async with conn.transaction():
                logger.debug(
                    "🔄 TRANSACTION STARTED",
                    extra={"request_id": request_id, "layer": "service"}
                )

                if validated_payload is None:
                    # Сохраняем невалидный запрос
                    id_uuid = uuid.uuid4()
                    status = "validation_error"

                    payload_json = json.dumps({
                        "_raw": raw_body,
                        "_content_type": content_type,
                        "_error": "Validation failed"
                    })

                    logger.debug(
                        "📝 SAVING INVALID REQUEST",
                        extra={
                            "request_id": request_id,
                            "id_uuid": str(id_uuid),
                            "status": status,
                            "layer": "service"
                        }
                    )

                    # 👇 Проверьте имя функции в БД!
                    result = await conn.fetchval("""
                        SELECT alpha_hook.save_callback_log(
                            $1::uuid,
                            $2::jsonb,
                            $3::alpha_hook.status,
                            $4::text
                        )
                    """, id_uuid, payload_json, status, "Validation failed")

                else:
                    # Сохраняем валидный запрос
                    id_uuid = validated_payload.mdOrder  # ← AlfaBankCallback имеет mdOrder
                    status = "pending"

                    payload_json = json.dumps(validated_payload.model_dump())

                    logger.debug(
                        "📝 SAVING VALID REQUEST",
                        extra={
                            "request_id": request_id,
                            "orderNumber": validated_payload.orderNumber,
                            "id_uuid": str(id_uuid),
                            "status": status,
                            "layer": "service"
                        }
                    )

                    result = await conn.fetchval("""
                        SELECT alpha_hook.save_callback_log(
                            $1::uuid,
                            $2::jsonb,
                            $3::alpha_hook.status,
                            $4::text
                        )
                    """, id_uuid, payload_json, status, None)

                logger.debug(
                    "✅ DATABASE OPERATION COMPLETED",
                    extra={
                        "request_id": request_id,
                        "db_result": result,
                        "layer": "service"
                    }
                )

                return {"success": True, "id": str(id_uuid), "status": status}

    except PostgresError as e:
        logger.error(
            "❌ DATABASE ERROR",
            extra={
                "request_id": request_id,
                "error": str(e),
                "error_type": "PostgresError",
                "layer": "service"
            }
        )
        raise DatabaseError(f"Database operation failed: {e}")

    except Exception as e:
        logger.exception(
            "🔥 UNEXPECTED ERROR IN DB SERVICE",
            extra={
                "request_id": request_id,
                "error": str(e),
                "error_type": type(e).__name__,
                "layer": "service"
            }
        )
        raise