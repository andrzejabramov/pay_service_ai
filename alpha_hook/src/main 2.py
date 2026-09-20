# alpha_hook/src/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from loguru import logger

from src.middleware.request_id import RequestIDMiddleware
from src.db.pools import init_pools, close_pools
from src.routers.sbp import router as sbp_router
from src.routers.webhook import router as webhook_router
from src.routers.merchant_profiles import router as merchant_profiles_router

from src.logger_config import setup_logger
from src.exceptions import (
    ValidationError,
    DatabaseError,
    WebhookProcessingError,
)
from src.middleware.request_id import request_id_ctx


@asynccontextmanager
async def lifespan(app):
    """Инициализация/закрытие пулов БД"""
    logger.info("🚀 Initializing database connection pools for alpha_hook...")
    setup_logger()
    await init_pools()
    yield
    logger.info("🛑 Closing database connection pools for alpha_hook...")
    await close_pools()


app = FastAPI(
    title="Alpha Hook Webhook Service",
    description="Обработка webhook от Альфа-Банка",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# --- Middleware ---
app.add_middleware(RequestIDMiddleware)

# --- Routers ---
app.include_router(webhook_router, prefix="/webhook")
app.include_router(sbp_router, prefix="/api/v1")
app.include_router(merchant_profiles_router, prefix="/api/v1")


# --- Exception handlers ---
@app.exception_handler(ValidationError)
async def validation_error_handler(request, exc: ValidationError):
    request_id = request_id_ctx.get()
    logger.warning(
        f"Validation error: {exc.message}",
        extra={"request_id": request_id, "details": exc.details},
    )
    return JSONResponse(
        status_code=400, content={"detail": exc.message, "details": exc.details}
    )


@app.exception_handler(DatabaseError)
async def database_error_handler(request, exc: DatabaseError):
    request_id = request_id_ctx.get()
    logger.error(
        f"Database error: {exc.message}",
        extra={"request_id": request_id, "details": exc.details},
    )
    return JSONResponse(
        status_code=503, content={"detail": "Database operation failed"}
    )


@app.exception_handler(WebhookProcessingError)
async def webhook_processing_error_handler(request, exc: WebhookProcessingError):
    request_id = request_id_ctx.get()
    logger.error(
        f"Processing error: {exc.message}",
        extra={"request_id": request_id, "details": exc.details},
    )
    return JSONResponse(
        status_code=500, content={"detail": "Internal processing error"}
    )


# --- Global exception handler (всегда 200 для банка) ---
@app.exception_handler(Exception)
async def generic_error_handler(request, exc: Exception):
    request_id = request_id_ctx.get()
    logger.exception(f"Unexpected error: {exc}", extra={"request_id": request_id})
    return JSONResponse(
        status_code=200,  # ← Всегда 200! Банк не должен повторять
        content={"status": "ok", "message": "Callback accepted (error logged)"},
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
