from fastapi import APIRouter, HTTPException, Header, Depends
from typing import Optional
from pydantic import BaseModel, EmailStr
from app.core.dependencies import get_auth_repo, get_user_repo
from app.services.auth_service import AuthService
from app.schemas.user import UserCreate

router = APIRouter()


def _get_auth_service() -> AuthService:
    return AuthService(auth_repo=get_auth_repo(), user_repo=get_user_repo())


# ── Request Schemas ──────────────────────────────────

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class SignupRequest(BaseModel):
    email: EmailStr
    login_id: str
    password: str
    full_name: str
    branch_id: Optional[str] = None
    language: str = "ko"

class RefreshRequest(BaseModel):
    refresh_token: str


# ── Endpoints ────────────────────────────────────────

@router.post("/login")
async def login(body: LoginRequest):
    try:
        service = _get_auth_service()
        return await service.login(body.email, body.password)
    except Exception as e:
        raise HTTPException(status_code=401, detail="로그인에 실패했습니다. 이메일 또는 비밀번호를 확인하세요.")


@router.post("/signup", status_code=201)
async def signup(body: SignupRequest):
    try:
        service = _get_auth_service()
        user_data = UserCreate(
            email=body.email,
            login_id=body.login_id,
            password=body.password,
            full_name=body.full_name,
            branch_id=body.branch_id,
            language=body.language,
        )
        return await service.signup(user_data)
    except Exception as e:
        if "already" in str(e).lower() or "duplicate" in str(e).lower():
            raise HTTPException(status_code=400, detail="이미 등록된 이메일입니다.")
        raise HTTPException(status_code=400, detail=f"회원가입 실패: {str(e)}")


@router.post("/logout")
async def logout(authorization: Optional[str] = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="인증 토큰이 누락되었습니다.")
    token = authorization.replace("Bearer ", "")
    try:
        service = _get_auth_service()
        return await service.logout(token)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/refresh")
async def refresh(body: RefreshRequest):
    try:
        service = _get_auth_service()
        return await service.refresh(body.refresh_token)
    except Exception as e:
        raise HTTPException(status_code=401, detail="토큰 갱신에 실패했습니다.")


@router.get("/me")
async def get_me(authorization: Optional[str] = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="인증 토큰이 누락되었습니다.")
    token = authorization.replace("Bearer ", "")
    try:
        service = _get_auth_service()
        return await service.get_current_auth_user(token)
    except Exception as e:
        raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다.")
