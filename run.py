"""
Launcher Script for Multilingual Translation Studio
Usage: python run.py
"""

import os
import sys
import uvicorn

if __name__ == "__main__":
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8000"))

    print("=" * 72)
    print("NEURAL TRANSLATION STUDIO - STARTING WEBSERVER")
    print("=" * 72)
    print(f"Server URL           : http://{host}:{port}")
    print(f"API Documentation    : http://{host}:{port}/docs")
    print(f"Alternative API Docs : http://{host}:{port}/redoc")
    print(f"Health Check         : http://{host}:{port}/api/v1/health")
    print("=" * 72)

    uvicorn.run("app.main:app", host=host, port=port, reload=False)
