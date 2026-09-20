# alpha_hook/src/middleware/request_id.py
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from contextvars import ContextVar

# Глобальный context для хранения request_id (доступен во всех слоях)
request_id_ctx: ContextVar[str] = ContextVar("request_id", default="")


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Добавляет X-Request-ID к каждому запросу.

    Сохраняет в:
    1. contextvars (доступно через request_id_ctx.get() в любом слое)
    2. request.state (доступно через request.state.request_id в хендлерах)
    3. Response headers (X-Request-ID в ответе)
    """

    async def dispatch(self, request: Request, call_next):
        # Берём из заголовков или генерируем новый
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())

        # Сохраняем в context (с proper token management)
        token = request_id_ctx.set(request_id)

        try:
            # Сохраняем в request.state (удобно для хендлеров)
            request.state.request_id = request_id

            # Вызываем следующий middleware/хендлер
            response = await call_next(request)

            # Добавляем в ответ
            response.headers["X-Request-ID"] = request_id

            return response
        finally:
            # 🔥 ВАЖНО: Сбрасываем context (защита от утечек в async)
            request_id_ctx.reset(token)