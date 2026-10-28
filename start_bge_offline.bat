@echo off
cd /d "%~dp0"
set HF_HUB_OFFLINE=1
set TRANSFORMERS_OFFLINE=1
if not defined BGE_MODEL_PATH (
 echo Set BGE_MODEL_PATH to your local BGE-M3 folder first.
 pause
 exit /b 1
)
where py >nul 2>nul
if errorlevel 1 (python -m uvicorn python_backend.server:app --host 127.0.0.1 --port 8000) else (py -3 -m uvicorn python_backend.server:app --host 127.0.0.1 --port 8000)
pause
