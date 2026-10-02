from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.ai import router as ai_router
from app.api.routes.analysis import router as analysis_router
from app.api.routes.auth import router as auth_router
from app.api.routes.projects import router as projects_router
from app.api.routes.reports import router as reports_router
from app.core.config import settings

app = FastAPI(
    title="CodeGuard AI",
    version="0.1.0",
    description="Code analysis, security scanning, and AI-assisted review platform.",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(projects_router, prefix="/api/projects", tags=["projects"])
app.include_router(analysis_router, prefix="/api/analysis", tags=["analysis"])
app.include_router(ai_router, prefix="/api/ai", tags=["ai"])
app.include_router(reports_router, prefix="/api/reports", tags=["reports"])


@app.get("/health")
def health_check() -> dict:
    return {"success": True, "status": "ok"}
