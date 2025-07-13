#!/usr/bin/env python3

from fastapi import FastAPI
import uvicorn

app = FastAPI(title="Simple Test")

@app.get("/")
async def root():
    return {"message": "Simple FastAPI is working"}

@app.get("/test")
async def test():
    return {"test": "passed", "framework": "FastAPI"}

if __name__ == "__main__":
    print("Starting simple FastAPI server...")
    uvicorn.run(app, host="0.0.0.0", port=8003, log_level="info") 