from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.api.endpoints import tasks, notices, auth, admin, users, dashboard, attendance, opinions, notifications, files

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CORS 설정: 모든 도메인에서의 접근을 허용합니다 (시연용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Global Exception Handler ────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """예상치 못한 에러를 통일된 형식으로 반환합니다."""
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "서버 내부 오류가 발생했습니다.",
            }
        },
    )


# 라우터 등록: 각 기능별로 분리된 API 엔드포인트를 연결합니다.
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["Auth"])
app.include_router(tasks.router, prefix=f"{settings.API_V1_STR}/tasks", tags=["Tasks"])
app.include_router(notices.router, prefix=f"{settings.API_V1_STR}/notices", tags=["Notices"])
app.include_router(admin.router, prefix=f"{settings.API_V1_STR}/admin", tags=["Admin"])
app.include_router(users.router, prefix=f"{settings.API_V1_STR}/users", tags=["Users"])
app.include_router(dashboard.router, prefix=f"{settings.API_V1_STR}/dashboard", tags=["Dashboard"])
app.include_router(attendance.router, prefix=f"{settings.API_V1_STR}/attendance", tags=["Attendance"])
app.include_router(opinions.router, prefix=f"{settings.API_V1_STR}/opinions", tags=["Opinions"])
app.include_router(notifications.router, prefix=f"{settings.API_V1_STR}/notifications", tags=["Notifications"])
app.include_router(files.router, prefix=f"{settings.API_V1_STR}/files", tags=["Files"])

@app.get("/")
def root():
    """서버 루트 경로 접속 시 환영 메시지를 반환합니다."""
    return {"message": "Welcome to Task Server API"}

@app.get("/health")
def health_check():
    """서버 상태를 확인하기 위한 헬스체크 엔드포인트입니다."""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    import os
    # Render와 같은 환경에서 PORT 환경 변수를 사용하도록 설정합니다.
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
