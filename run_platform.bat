@echo off
echo =======================================================================
echo  DROSIA: Drone Security Intelligence ^& Analytics Platform (Version 1.0)
echo =======================================================================
echo Starting FastAPI Backend and Serving Tactical Intelligence HUD...
echo Open your browser at: http://localhost:8000
echo.
if exist ".venv\Scripts\python.exe" (
    .venv\Scripts\python.exe backend\run.py
) else (
    py backend\run.py
)
pause
