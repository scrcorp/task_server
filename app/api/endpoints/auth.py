from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from app.services.auth_service import AuthService
from app.core.dependencies import get_auth_service
from app.core.security import get_current_user
from app.schemas.user import User, UserCreate

router = APIRouter()


# -- Request Schemas --

class LoginRequest(BaseModel):
    login_id: str
    password: str

class SignupRequest(BaseModel):
    email: EmailStr
    login_id: str
    password: str
    full_name: str
    company_code: str
    language: str = "en"

class RefreshRequest(BaseModel):
    refresh_token: str

class VerifyEmailRequest(BaseModel):
    email: EmailStr
    code: str

class SendVerificationRequest(BaseModel):
    email: EmailStr


# -- Endpoints --

@router.post("/login")
async def login(body: LoginRequest, service: AuthService = Depends(get_auth_service)):
    try:
        return await service.login(body.login_id, body.password)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid login ID or password.")


@router.post("/signup", status_code=201)
async def signup(body: SignupRequest, service: AuthService = Depends(get_auth_service)):
    try:
        user_data = UserCreate(
            email=body.email,
            login_id=body.login_id,
            password=body.password,
            full_name=body.full_name,
            company_id="temp",
            language=body.language,
        )
        return await service.signup(user_data, company_code=body.company_code)
    except Exception as e:
        msg = str(e)
        if "not verified" in msg.lower():
            raise HTTPException(status_code=400, detail=msg)
        if "already" in msg.lower() or "duplicate" in msg.lower() or "taken" in msg.lower():
            raise HTTPException(status_code=400, detail=msg)
        if "company code" in msg.lower():
            raise HTTPException(status_code=400, detail=msg)
        raise HTTPException(status_code=400, detail="Signup failed.")


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user),
    service: AuthService = Depends(get_auth_service),
):
    return await service.logout()


@router.post("/refresh")
async def refresh(body: RefreshRequest, service: AuthService = Depends(get_auth_service)):
    try:
        return await service.refresh(body.refresh_token)
    except Exception:
        raise HTTPException(status_code=401, detail="Token refresh failed.")


@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/verify-email")
async def verify_email(
    body: VerifyEmailRequest,
    service: AuthService = Depends(get_auth_service),
):
    try:
        return await service.verify_email(body.email, body.code)
    except Exception as e:
        msg = str(e)
        if "too many" in msg.lower():
            raise HTTPException(status_code=429, detail=msg)
        raise HTTPException(status_code=400, detail="Invalid or expired verification code.")


@router.post("/send-verification")
async def send_verification(
    body: SendVerificationRequest,
    service: AuthService = Depends(get_auth_service),
):
    try:
        return await service.send_verification_email(body.email)
    except Exception as e:
        msg = str(e)
        if "too many" in msg.lower():
            raise HTTPException(status_code=429, detail=msg)
        if "already registered" in msg.lower():
            raise HTTPException(status_code=400, detail=msg)
        raise HTTPException(status_code=500, detail="Failed to send verification email.")
