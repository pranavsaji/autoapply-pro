# apps/api/main.py
from fastapi import FastAPI
from fastapi.responses import RedirectResponse, JSONResponse
from apps.api.settings import settings
from apps.api.routers import profile, discovery, apply, admin

app = FastAPI(title="AutoApply Pro API")

# Routers
app.include_router(profile.router,  prefix="/profile",   tags=["profile"])
app.include_router(discovery.router, prefix="/discovery", tags=["discovery"])
app.include_router(apply.router,     prefix="/apply",     tags=["apply"])
app.include_router(admin.router,     prefix="/admin",     tags=["admin"])

# Root: basic info
@app.get("/", include_in_schema=False)
def root():
    return JSONResponse({
        "name": "AutoApply Pro",
        "version": "0.1.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/admin/health"
    })

# Optional: redirect /home to docs
@app.get("/home", include_in_schema=False)
def home():
    return RedirectResponse(url="/docs")
