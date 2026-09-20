from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime


class MerchantProfileCreate(BaseModel):
    user_id: UUID = Field(..., description="UUID исполнителя из сервиса users")
    terminal_id: str = Field(
        ..., min_length=1, description="ID терминала от Альфа-Банка"
    )
    qr_code_id: Optional[str] = Field(None, description="ID QR-кода (опционально)")
    merchant_name: Optional[str] = Field(None, description="Название для удобства")
    region: Optional[str] = Field(None, description="Регион обслуживания")


class MerchantProfileRead(BaseModel):
    id: UUID
    user_id: UUID
    terminal_id: str
    qr_code_id: Optional[str] = None
    merchant_name: Optional[str] = None
    region: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class BindQrRequest(BaseModel):
    qr_code_id: str = Field(..., min_length=1, description="ID QR-кода для привязки")
