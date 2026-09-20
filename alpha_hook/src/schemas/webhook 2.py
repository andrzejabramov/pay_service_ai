# alpha_hook/src/schemas/webhook.py
"""
Pydantic схемы для валидации входящих вебхуков от Альфа-Банка
"""

from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing import Optional
import uuid


class AlfaBankCallback(BaseModel):
    """
    Схема входящего webhook от Альфа-Банка.
    Формат: POST, application/x-www-form-urlencoded
    """
    model_config = ConfigDict(extra="allow")  # разрешить доп. поля после согласования

    # Обязательные поля (из документации)
    mdOrder: str = Field(..., description="ID транзакции в шлюзе банка")
    orderNumber: str = Field(..., description="ID заказа/водителя в нашей системе")
    operation: str = Field(..., description="Тип события: deposited, approved, etc.")
    status: int = Field(..., description="1=успех, 0=ошибка")
    checksum: str = Field(..., description="Контрольная сумма для проверки подлинности")

    # Дополнительные поля (будут добавлены после согласования с поддержкой)
    amount: Optional[int] = Field(None, description="Сумма в копейках")
    callbackCreationDate: Optional[str] = Field(None, description="Дата создания уведомления")
    paymentDate: Optional[str] = Field(None, description="Дата оплаты")
    approvalCode: Optional[str] = Field(None, description="Код авторизации")
    paymentRefNum: Optional[str] = Field(None, description="RRN транзакции")

    @field_validator('status')
    @classmethod
    def validate_status(cls, v: int) -> int:
        """Проверить, что status — 0 или 1"""
        if v not in (0, 1):
            raise ValueError(f"status must be 0 or 1, got: {v}")
        return v

    @field_validator('mdOrder')
    @classmethod
    def validate_md_order(cls, v: str) -> str:
        """Проверить, что mdOrder не пустой (UUID проверим позже, т.к. формат может быть разный)"""
        if not v or not v.strip():
            raise ValueError("mdOrder cannot be empty")
        return v.strip()

    @property
    def is_successful_payment(self) -> bool:
        """Успешная оплата = deposited + status=1"""
        return self.operation == "deposited" and self.status == 1

    @property
    def driver_id(self) -> str:
        """Алиас для orderNumber"""
        return self.orderNumber

    @property
    def amount_rub(self) -> Optional[float]:
        """Конвертация копеек в рубли"""
        return self.amount / 100.0 if self.amount else None


class ApiResponse(BaseModel):
    """Стандартный ответ API"""
    status: str = Field(..., description="Статус обработки")
    message: str = Field(..., description="Сообщение")
    request_id: Optional[str] = Field(None, description="ID запроса для трассировки")