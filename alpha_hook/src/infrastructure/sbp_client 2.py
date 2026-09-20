# alpha_hook/src/infrastructure/sbp_client.py
import json
import ssl
from pathlib import Path
from typing import Dict, Any
import httpx
from src.infrastructure.sbp.crypto import sign_body


class SBPClient:
    """
    Асинхронный клиент для API СБП Альфа-Банка.
    Автоматически: формирует JSON, подписывает тело, добавляет заголовки mTLS.
    """

    def __init__(
        self,
        endpoint: str,
        alias: str,
        term_no: str,
        mtls_cert_path: Path,  # ← переименовал для ясности
        mtls_key_path: Path,  # ← переименовал для ясности
        signing_key_path: Path,  # ← добавляем путь к ключу для подписи
        ca_path: Path,
        timeout: float = 30.0,
    ):
        self.endpoint = endpoint.rstrip("/")
        self.alias = alias
        self.term_no = term_no
        self.mtls_cert_path = mtls_cert_path
        self.mtls_key_path = mtls_key_path
        self.signing_key_path = signing_key_path
        self.ca_path = ca_path
        self.timeout = timeout

    def _build_client(self) -> httpx.AsyncClient:
        # Создаём SSL-контекст с вашим CA-бандлом
        ssl_ctx = ssl.create_default_context(cafile=str(self.ca_path))
        # Отключаем проверку имени хоста (нужно для тестовых IP-адресов банка)
        ssl_ctx.check_hostname = False

        return httpx.AsyncClient(
            cert=(str(self.mtls_cert_path), str(self.mtls_key_path)),
            verify=ssl_ctx,
            timeout=self.timeout,
        )

    async def post(self, command: str, payload: Dict[str, Any]) -> httpx.Response:
        # 1. Формируем тело запроса
        body_dict = {"command": command, "TermNo": self.term_no, **payload}
        body = json.dumps(body_dict, separators=(",", ":"), ensure_ascii=False)

        # 2. Подписываем тело КЛЮЧОМ ДЛЯ ПОДПИСИ
        signature = sign_body(body, self.signing_key_path)

        # 3. Заголовки
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "key-name": self.alias,
            "Authorization": signature,
        }

        # 4. Отправляем
        async with self._build_client() as client:
            return await client.post(
                self.endpoint, content=body.encode("utf-8"), headers=headers
            )

    async def test_pay_qr(self, qrc_id: str, status: str = "ACWP") -> httpx.Response:
        """Эмуляция оплаты (только тест). status: "ACWP" или "RJCT" """
        return await self.post("TestPayQR", {"qrcId": qrc_id, "Status": status})

    async def get_qrc_status(self, qrc_id: str) -> httpx.Response:
        """Проверка статуса платежа (лимит 4 запроса/мин на тесте)"""
        return await self.post("GetQRCstatus", {"qrcId": qrc_id})
