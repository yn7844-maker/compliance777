@echo off
setlocal
cd /d "%~dp0"
set HF_HUB_OFFLINE=1
set TRANSFORMERS_OFFLINE=1
if not defined BGE_MODEL_PATH set "BGE_MODEL_PATH=%~dp0models\bge-m3"
if not exist "%BGE_MODEL_PATH%\config.json" (
 echo Model missing. Run:
 echo python -m pip install -r python_backend/requirements.txt
 echo python -m python_backend.download_model --output models/bge-m3
 pause
 exit /b 1
)
if exist "%~dp0.venv\Scripts\python.exe" (
 "%~dp0.venv\Scripts\python.exe" -m uvicorn python_backend.server:app --host 127.0.0.1 --port 8000
 pause
 exit /b
)
where py >nul 2>nul
if errorlevel 1 (python -m uvicorn python_backend.server:app --host 127.0.0.1 --port 8000) else (py -3 -m uvicorn python_backend.server:app --host 127.0.0.1 --port 8000)
pause
