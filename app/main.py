from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.api.endpoints import auth, assignments, daily_checklists, notices, admin, users, dashboard, attendance, opinions, notifications, files, setup

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CORS
cors_origins = (
    ["*"]
    if settings.CORS_ORIGINS == "*"
    else [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=settings.CORS_ORIGINS != "*",
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Global Exception Handler ────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "Internal server error.",
            }
        },
    )


# Router registration
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["Auth"])
app.include_router(assignments.router, prefix=f"{settings.API_V1_STR}/assignments", tags=["Assignments"])
app.include_router(daily_checklists.router, prefix=f"{settings.API_V1_STR}/daily-checklists", tags=["Daily Checklists"])
app.include_router(notices.router, prefix=f"{settings.API_V1_STR}/notices", tags=["Notices"])
app.include_router(admin.router, prefix=f"{settings.API_V1_STR}/admin", tags=["Admin"])
app.include_router(users.router, prefix=f"{settings.API_V1_STR}/users", tags=["Users"])
app.include_router(dashboard.router, prefix=f"{settings.API_V1_STR}/dashboard", tags=["Dashboard"])
app.include_router(attendance.router, prefix=f"{settings.API_V1_STR}/attendance", tags=["Attendance"])
app.include_router(opinions.router, prefix=f"{settings.API_V1_STR}/opinions", tags=["Opinions"])
app.include_router(notifications.router, prefix=f"{settings.API_V1_STR}/notifications", tags=["Notifications"])
app.include_router(files.router, prefix=f"{settings.API_V1_STR}/files", tags=["Files"])
app.include_router(setup.router, prefix=f"{settings.API_V1_STR}/setup", tags=["Setup"])

@app.get("/")
def root():
    return {"message": "Welcome to Task Server API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
