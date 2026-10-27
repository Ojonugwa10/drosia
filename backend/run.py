"""
Startup runner script for Drosia Backend Server
"""

import os
import sys

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import uvicorn

if __name__ == "__main__":
    print("=" * 70)
    print(" DROSIA: Drone Security Intelligence & Analytics Platform v1.0")
    print(" Starting Local Intelligence & Tactical GIS Server...")
    print(" Server URL: http://localhost:8000")
    print("=" * 70)
    uvicorn.run("backend.app.main:app", host="127.0.0.1", port=8000, reload=False)
