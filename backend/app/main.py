"""
OCR Platform - Main Application Entry Point

This module initializes the FastAPI application, configures middleware,
registers API routers, and sets up logging.

Author: Your Name
Created: 2024
License: MIT
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.ocr import router as ocr_router
from app.api.export import router as export_router
from app.api.batch import router as batch_router
import os
import logging
import sys

# Configure logging with timestamp, level, and message format
# Outputs to stdout for container-friendly logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Create FastAPI application instance with metadata
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    description="Enterprise-grade OCR platform with dual-engine support",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS (Cross-Origin Resource Sharing) middleware
# Allows frontend applications from different origins to access the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Local development
        "http://localhost:3000",
        "https://ocr-platform.vercel.app",  # Production frontend
        "https://ocr-platform-git-main-rohits-projects-4a9c7d0b.vercel.app",  # Vercel preview
        "https://ocr-platform-lz5n9gor-rohits-projects-4a9c7d0b.vercel.app",  # Vercel preview
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, DELETE, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Ensure upload directory exists for storing processed files
# Creates directory with all parent directories if they don't exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
logger.info(f"Upload directory created/verified: {settings.UPLOAD_DIR}")

# Register API routers with their respective endpoints
# Each router handles a specific domain of functionality
app.include_router(ocr_router)      # /api/ocr/* - Single document OCR
app.include_router(export_router)   # /api/export/* - Export operations
app.include_router(batch_router)    # /api/batch/* - Batch processing
logger.info("All API routers registered successfully")


@app.on_event("startup")
async def startup_event():
    """Log startup information"""
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    logger.info(f"OCR Engine: {settings.DEFAULT_OCR_ENGINE}")
    logger.info("Application startup complete")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT
    }
