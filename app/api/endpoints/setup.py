import traceback
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from app.core.supabase import supabase
from app.core.password import hash_password

router = APIRouter()


class InitRequest(BaseModel):
    company_code: str = "SCR"
    company_name: str = "SCR"
    admin_login_id: str = "admin"
    admin_password: str = "admin1234"
    admin_email: str = "admin@scr.com"
    admin_name: str = "Admin"


@router.post("/init")
def initialize_system(req: InitRequest = InitRequest()):
    """Create initial company + admin account. Idempotent."""
    try:
        return _do_init(req)
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": str(e)})


def _do_init(req: InitRequest):
    # 1. Check if company already exists
    existing = (
        supabase.table("companies")
        .select("id")
        .eq("code", req.company_code)
        .limit(1)
        .execute()
    )
    if existing.data:
        company_id = existing.data[0]["id"]
    else:
        res = (
            supabase.table("companies")
            .insert({"code": req.company_code, "name": req.company_name})
            .execute()
        )
        company_id = res.data[0]["id"]

    # 2. Check if admin user already exists
    existing_user = (
        supabase.table("users")
        .select("id, login_id")
        .eq("login_id", req.admin_login_id)
        .limit(1)
        .execute()
    )
    if existing_user.data:
        raise HTTPException(
            status_code=409,
            detail=f"User '{req.admin_login_id}' already exists.",
        )

    # 3. Create admin user
    user_data = {
        "company_id": company_id,
        "email": req.admin_email,
        "login_id": req.admin_login_id,
        "password_hash": hash_password(req.admin_password),
        "full_name": req.admin_name,
        "role": "admin",
        "status": "active",
        "language": "en",
        "email_verified": True,
    }
    user_res = supabase.table("users").insert(user_data).execute()

    return {
        "message": "System initialized successfully.",
        "company": {"id": company_id, "code": req.company_code},
        "admin": {
            "id": user_res.data[0]["id"],
            "login_id": req.admin_login_id,
        },
    }
