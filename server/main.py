# Entry point for the server/FastAPI application

from app.core.app import app
from app.api.routes import traceroute

# Include routers
app.include_router(traceroute.router, prefix="/api/v1")

@app.get("/")
async def root():
    return {
        "message": "Welcome to PktPath API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}