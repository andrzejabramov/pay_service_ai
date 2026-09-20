from fastapi import APIRouter, Depends, HTTPException, status
from asyncpg import Pool
from asyncpg.exceptions import UniqueViolationError
from uuid import UUID
from typing import List
from loguru import logger

from alpha_hook.src.dependencies.db import get_db_pool
from alpha_hook.src.dependencies.auth import require_fintech_manager
from alpha_hook.src.schemas.merchant_profiles import (
    MerchantProfileCreate,
    MerchantProfileRead,
    BindQrRequest,
)

router = APIRouter(prefix="/admin/merchant-profiles", tags=["Admin: Merchant Profiles"])


@router.post(
    "/", response_model=MerchantProfileRead, status_code=status.HTTP_201_CREATED
)
async def create_merchant_profile(
    data: MerchantProfileCreate,
    pool: Pool = Depends(get_db_pool),
    admin: dict = Depends(require_fintech_manager),
):
    logger.info(
        f"Admin {admin['user_id']} creating profile for user {data.user_id}, terminal {data.terminal_id}"
    )
    try:
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM alpha_hook.create_merchant_profile($1, $2, $3, $4, $5)",
                data.user_id,
                data.terminal_id,
                data.qr_code_id,
                data.merchant_name,
                data.region,
            )
        return MerchantProfileRead(**dict(row))
    except UniqueViolationError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Terminal '{data.terminal_id}' already exists",
        )
    except Exception as e:
        logger.error(f"Failed to create merchant profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error"
        )


@router.get("/by-user/{user_id}", response_model=List[MerchantProfileRead])
async def get_profiles_by_user(
    user_id: UUID,
    pool: Pool = Depends(get_db_pool),
    admin: dict = Depends(require_fintech_manager),
):
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT * FROM alpha_hook.get_merchant_profile_by_user($1)", user_id
        )
    return [MerchantProfileRead(**dict(row)) for row in rows]


@router.patch("/{terminal_id}/bind-qr", response_model=MerchantProfileRead)
async def bind_qr_code(
    terminal_id: str,
    data: BindQrRequest,
    pool: Pool = Depends(get_db_pool),
    admin: dict = Depends(require_fintech_manager),
):
    logger.info(
        f"Admin {admin['user_id']} binding QR {data.qr_code_id} to terminal {terminal_id}"
    )
    try:
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM alpha_hook.bind_qr_to_terminal($1, $2)",
                terminal_id,
                data.qr_code_id,
            )
        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Active terminal '{terminal_id}' not found",
            )
        return MerchantProfileRead(**dict(row))
    except Exception as e:
        logger.error(f"Failed to bind QR code: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error"
        )


@router.delete("/{terminal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_profile(
    terminal_id: str,
    pool: Pool = Depends(get_db_pool),
    admin: dict = Depends(require_fintech_manager),
):
    async with pool.acquire() as conn:
        result = await conn.execute(
            "UPDATE alpha_hook.merchant_profiles SET is_active = false, updated_at = now() WHERE terminal_id = $1 AND is_active = true",
            terminal_id,
        )
    if result == "UPDATE 0":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Active terminal '{terminal_id}' not found",
        )
    logger.info(f"Admin {admin['user_id']} deactivated terminal {terminal_id}")
    return None
