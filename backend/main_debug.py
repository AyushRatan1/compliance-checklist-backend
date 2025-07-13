#!/usr/bin/env python3

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
logger.info("Loading environment variables...")
load_dotenv()

# Initialize FastAPI app
logger.info("Initializing FastAPI app...")
app = FastAPI(
    title="Debug Compliance Checklist Generator API",
    description="Debug version",
    version="1.0.0"
)

# Configure CORS
logger.info("Configuring CORS...")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info("Setting up endpoints...")

@app.get("/")
async def root():
    logger.info("Root endpoint accessed")
    return {
        "message": "Debug Professional Compliance Checklist Generator API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    logger.info("Health check requested")
    return {
        "status": "healthy",
        "aws_configured": bool(os.getenv("AWS_ACCESS_KEY_ID")),
        "message": "Debug health check"
    }

@app.get("/test")
async def test():
    logger.info("Test endpoint accessed")
    return {"test": "passed", "message": "Debug endpoint working"}

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting uvicorn server...")
    port = int(os.getenv("PORT", 8004))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info") 