"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings

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
