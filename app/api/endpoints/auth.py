from fastapi import APIRouter, HTTPException, Header
from typing import Optional
from app.core.supabase import supabase

router = APIRouter()

@router.post("/login")
def login(email: str, password: str):
    """
    Supabase Auth를 이용한 로그인
    성공 시 access_token을 반환합니다.
    """
    try:
        response = supabase.auth.sign_in_with_password({"email": email, "password": password})
        return response
    except Exception as e:
        raise HTTPException(status_code=401, detail="로그인에 실패했습니다. 이메일 또는 비밀번호를 확인하세요.")

@router.get("/me")
def get_current_user(authorization: Optional[str] = Header(None)):
    """
    현재 로그인된 사용자의 정보를 가져옵니다.
    Header에 'Authorization: Bearer <token>'이 필요합니다.
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="인증 토큰이 누락되었습니다.")
    
    token = authorization.replace("Bearer ", "")
    try:
        user = supabase.auth.get_user(token)
        return user
    except Exception as e:
        raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다.")
