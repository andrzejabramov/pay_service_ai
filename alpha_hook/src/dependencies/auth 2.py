import jwt
from fastapi import Depends, HTTPException, status, Request
from asyncpg import Pool
from alpha_hook.src.core.config import settings
from alpha_hook.src.dependencies.db import get_db_pool


async def require_fintech_manager(
    request: Request, pool: Pool = Depends(get_db_pool)
) -> dict:
    """
    Проверяет JWT токен и наличие роли 'fintech_manager'.
    Возвращает {"user_id": str}
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header",
        )

    token = auth_header.split(" ")[1]
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing sub",
            )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )

    # Проверка роли через БД (один быстрый запрос)
    has_role = await pool.fetchval(
        "SELECT alpha_hook.check_user_has_role($1, 'fintech_manager')", user_id
    )
    if not has_role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: 'fintech_manager' role required",
        )

    return {"user_id": user_id}
