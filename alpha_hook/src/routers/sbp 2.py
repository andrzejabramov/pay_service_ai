# src/routers/sbp.py
from fastapi import (
    APIRouter,
    HTTPException,
    Query,
    Request,
    BackgroundTasks,
    Header,
)
from pathlib import Path
import logging
from src.infrastructure.sbp_client import SBPClient
from src.infrastructure.sbp.crypto import verify_nspk_signature

router = APIRouter(prefix="/sbp", tags=["SBP C2B"])
logger = logging.getLogger(__name__)


# Временная фабрика (на следующем шаге вынесем в FastAPI Depends)
def get_client() -> SBPClient:
    return SBPClient(
        endpoint="https://217.12.103.132:2443/fsCryptoProxy",
        alias="0107029316_test_03.06.2028",
        term_no="30005150",
        mtls_cert_path=Path("certs/mtls/0107029316_test_mtls.crt"),
        mtls_key_path=Path("certs/mtls/0107029316_test_mtls.key"),
        signing_key_path=Path("certs/signing/client.key"),
        ca_path=Path("certs/ca/ca-bundle.crt"),
    )


@router.post("/create-qr")
async def create_qr(amount: int = Query(default=10000, description="Сумма в копейках")):
    client = get_client()
    resp = await client.post(
        "GetQRCd", {"qrcType": "01", "currency": "RUB", "amount": str(amount)}
    )
    data = resp.json()
    if data.get("ErrorCode") != 0:
        raise HTTPException(status_code=400, detail=data)
    return {"qrc_id": data["qrcId"], "image": data.get("image")}


@router.get("/status/{qrc_id}")
async def get_status(qrc_id: str):
    client = get_client()
    resp = await client.get_qrc_status(qrc_id)
    data = resp.json()
    if data.get("ErrorCode") != 0:
        raise HTTPException(status_code=400, detail=data)
    return data


@router.post("/pay/{qrc_id}")
async def emulate_payment(
    qrc_id: str, status: str = Query(default="ACWP", regex="^(ACWP|RJCT)$")
):
    """Эмуляция оплаты (только для тестового контура). status: "ACWP" или "RJCT" """
    client = get_client()
    resp = await client.test_pay_qr(qrc_id, status=status)
    data = resp.json()
    if data.get("ErrorCode") != 0:
        raise HTTPException(status_code=400, detail=data)
    return data


@router.post("/webhook", status_code=200)
async def sbp_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    x_signature: str | None = Header(default=None, alias="X-Signature"),
    x_certificate: str | None = Header(default=None, alias="X-Certificate"),
):
    """
    Вебхук для приёма подписанных уведомлений от НСПК.

    Заголовки:
    - X-Signature: Base64(GOST-подпись)
    - X-Certificate: (опционально) PEM-сертификат НСПК или ID для загрузки
    """
    try:
        # 1. Читаем raw body для верификации (важно: именно байты, как пришли)
        body_bytes = await request.body()
        payload = await request.json()

        qrc_id = payload.get("qrcId")
        status = payload.get("status")

        # 2. Если подпись есть — проверяем
        if x_signature:
            is_valid = verify_nspk_signature(
                body_bytes=body_bytes,
                signature_b64=x_signature,
                certificate_pem=x_certificate,  # или загрузим из хранилища по ID
            )
            if not is_valid:
                logger.warning(f"❌ Invalid signature for qrc_id={qrc_id}")
                # Возвращаем 200, но с флагом ошибки — НСПК не будет повторять, но мы зафиксируем
                return {
                    "status": "rejected",
                    "reason": "invalid_signature",
                    "qrcId": qrc_id,
                }
            logger.info(f"✅ Signature verified for qrc_id={qrc_id}")

        logger.info(f"🔔 Webhook received: qrc_id={qrc_id}, status={status}")

        # 3. Фоновая обработка (только если подпись валидна или отсутствует в тесте)
        background_tasks.add_task(process_sbp_notification, payload)

        return {"status": "accepted", "qrcId": qrc_id}

    except Exception as e:
        logger.error(f"❌ Webhook error: {e}", exc_info=True)
        return {"status": "error", "message": "internal_error"}


async def process_sbp_notification(payload: dict):
    """Фоновая обработка уведомления (не блокирует ответ банку)"""
    qrc_id = payload.get("qrcId")
    status = payload.get("status")

    # TODO:
    # 1. Проверить, есть ли такая транзакция в БД
    # 2. Обновить статус: UPDATE payments SET status = $1 WHERE qrc_id = $2
    # 3. Если статус финальный (ACWP/RJCT) — отправить событие в RabbitMQ
    # 4. Записать в аудит-лог

    logger.info(f"✅ Processed: {qrc_id} → {status}")
