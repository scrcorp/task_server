from fastapi import HTTPException, Header, Depends
from typing import Optional
from app.core.jwt import decode_token
from app.core.dependencies import get_user_repo
from app.schemas.user import User, UserRole
import jwt as pyjwt


async def get_current_user(authorization: Optional[str] = Header(None)) -> User:
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization token is missing.")

    token = authorization.replace("Bearer ", "")
    try:
        payload = decode_token(token)
        if payload.get("type") != "access":
            raise HTTPException(status_code=401, detail="Invalid token type.")
        user_id = payload["sub"]

        user_repo = get_user_repo()
        user = await user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User profile not found.")

        return user
    except pyjwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired.")
    except pyjwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token.")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")


def require_role(roles: list[UserRole]):
    async def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in roles:
            raise HTTPException(
                status_code=403,
                detail=f"Access denied. Required roles: {[r.value for r in roles]}",
            )
        return current_user
    return role_checker
