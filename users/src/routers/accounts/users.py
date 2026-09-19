import json
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    Body,
    UploadFile,
    File,
    Query,
)
from loguru import logger
from asyncpg import Pool
from uuid import UUID

from src.services.users import (
    UserService,
    bulk_create_users_from_file,
)
from src.db.redis import redis
from src.cache.user_cashe import (
    get_user_by_identifier_cached,
)
from src.utils.json_utils import maybe_json_loads, maybe_json_dumps
from src.dependencies.db import get_read_db_pool, get_write_db_pool
from src.dependencies.upload import validate_upload_file
from src.schemas.common import PaginatedResponse
from src.exceptions.exceptions import ValidationError, UserNotFound
from src.schemas.users import (
    UserCreate,
    UserUpdate,
    UserRead,
    BulkCreateRequest,
    BulkCreateResult,
    UploadResult,
    UserDetailRead,
)

router = APIRouter(tags=["Accounts: Users"])


# ✅ Отдельные фабрики для read и write
async def get_read_user_service(pool: Pool = Depends(get_read_db_pool)) -> UserService:
    return UserService(pool)


async def get_write_user_service(
    pool: Pool = Depends(get_write_db_pool),
) -> UserService:
    return UserService(pool)


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(
    user: UserCreate, service: UserService = Depends(get_write_user_service)
):
    return await service.create(user)


@router.get("/", response_model=PaginatedResponse[UserRead])
async def get_user_list(
    page: int = Query(1, ge=1, description="Номер страницы"),
    size: int = Query(50, ge=1, le=100, description="Размер страницы (макс. 100)"),
    service: UserService = Depends(get_read_user_service),
):
    return await service.get_paginated(page=page, size=size)


@router.patch("/{user_id}", response_model=UserRead)
async def update_user(
    user_id: UUID,
    user_update: UserUpdate = Body(
        examples=[{"is_active": False, "profile": {"key": "value"}}]
    ),
    service: UserService = Depends(get_write_user_service),
):
    return await service.update(
        user_id=user_id,
        profile=user_update.profile,
        is_active=user_update.is_active,
    )


@router.post("/bulk", response_model=BulkCreateResult)
async def bulk_create_users(
    request: BulkCreateRequest,
    service: UserService = Depends(get_write_user_service),
):
    try:
        result = await service.bulk_create_users(
            interface=request.interface, users=request.users
        )
        return result
    except ValueError as e:
        raise ValidationError("bulk_create", "users", str(e))


@router.post("/bulk/upload", response_model=UploadResult)
async def bulk_create_users_upload(file: UploadFile = Depends(validate_upload_file)):
    return await bulk_create_users_from_file(file)


@router.get("/by-identifier", response_model=UserDetailRead)
async def get_user_by_identifier(
    identifier: str = Query(
        ...,
        min_length=1,
        max_length=255,
        description="UUID, email, phone (+7...), or second_login",
    ),
    pool: Pool = Depends(get_read_db_pool),
):
    return await get_user_by_identifier_cached(identifier, pool)
