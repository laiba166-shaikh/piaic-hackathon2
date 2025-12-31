"""FastAPI application entry point."""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.backend.api.v1.tasks import router as tasks_router
from src.core.backend.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Create FastAPI application
app = FastAPI(
    title="Todo API",
    version="1.0.0",
    debug=settings.DEBUG
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,                   # Allow cookies (JWT)
    allow_methods=["*"],                      # Allow all HTTP methods
    allow_headers=["*"],                      # Allow all headers
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Todo API - Phase 2 Full-Stack Web Application"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


# Register API routers
app.include_router(tasks_router)
