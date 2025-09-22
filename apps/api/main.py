# apps/api/main.py
from fastapi import FastAPI
from apps.api.routers import profile, discovery, apply, admin

app = FastAPI(title="AutoApply Pro API")

app.include_router(profile.router,  prefix="/profile",   tags=["profile"])
app.include_router(discovery.router, prefix="/discovery", tags=["discovery"])
app.include_router(apply.router,     prefix="/apply",     tags=["apply"])
app.include_router(admin.router,     prefix="/admin",     tags=["admin"])
