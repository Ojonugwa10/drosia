"""
Main FastAPI Application Entrypoint for Drosia
Drone Security Intelligence & Analytics Platform — Version 1.0
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

from .routers.auth_router import router as auth_router
from .routers.projects_router import router as projects_router
from .routers.uploads_router import router as uploads_router
from .routers.analytics_router import router as analytics_router
from .routers.findings_router import router as findings_router
from .routers.reports_router import router as reports_router
from .routers.audit_router import router as audit_router


app = FastAPI(
    title="Drosia — Drone Security Intelligence & Analytics Platform",
    description="Transforms heterogeneous drone-operation data into validated, explainable, and actionable operational intelligence.",
    version="1.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API routers
app.include_router(auth_router)
app.include_router(projects_router)
app.include_router(uploads_router)
app.include_router(analytics_router)
app.include_router(findings_router)
app.include_router(reports_router)
app.include_router(audit_router)


@app.get("/api/v1/health")
def health_check():
    return {
        "status": "healthy",
        "platform": "Drosia Drone Security Intelligence & Analytics",
        "version": "1.0.0",
        "standardization": "Canonical Schema Active",
        "audit_chain": "Tamper-Evident SHA-256 Chaining Active",
    }


# Frontend static files mounting
frontend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend"))
if os.path.exists(frontend_path):
    # Mount frontend static directory
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
