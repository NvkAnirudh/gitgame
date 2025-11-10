"""
Git Quest FastAPI Application
Main entry point for the API server
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv

from app.api import auth, lessons, players, challenges, sessions

# Load environment variables
load_dotenv()

# Create FastAPI application
app = FastAPI(
    title="Git Quest API",
    description="Backend API for Git Quest - An Interactive Git Learning Adventure",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# CORS middleware configuration
origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health", tags=["health"])
async def health_check():
    """
    Health check endpoint
    """
    return {
        "status": "healthy",
        "service": "git-quest-api",
        "version": "1.0.0"
    }


# Root endpoint
@app.get("/", tags=["root"])
async def root():
    """
    Root endpoint - API information
    """
    return {
        "name": "Git Quest API",
        "version": "1.0.0",
        "description": "Backend API for Git Quest - An Interactive Git Learning Adventure",
        "docs": "/api/docs",
        "endpoints": {
            "auth": "/api/auth",
            "lessons": "/api/lessons",
            "players": "/api/players",
            "challenges": "/api/challenges",
            "sessions": "/api/sessions"
        }
    }


# Include API routers
app.include_router(auth.router, prefix="/api")
app.include_router(lessons.router, prefix="/api")
app.include_router(players.router, prefix="/api")
app.include_router(challenges.router, prefix="/api")
app.include_router(sessions.router, prefix="/api")


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Global exception handler for unhandled errors
    """
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error": str(exc) if os.getenv("DEBUG", "False") == "True" else "An error occurred"
        }
    )


# Startup event
@app.on_event("startup")
async def startup_event():
    """
    Run on application startup
    """
    print("🚀 Git Quest API starting up...")
    print(f"📖 Documentation available at: http://localhost:8000/api/docs")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """
    Run on application shutdown
    """
    print("👋 Git Quest API shutting down...")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
