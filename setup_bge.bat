@echo off
setlocal
set HF_HUB_OFFLINE=0
set TRANSFORMERS_OFFLINE=0
cd /d "%~dp0"
echo BGE-M3 local setup - Python 3.10+ required.
echo This installs dependencies and downloads a multi-GB model once.
where py >nul 2>nul
if errorlevel 1 (python -m venv .venv) else (py -3 -m venv .venv)
if errorlevel 1 goto failed
"%~dp0.venv\Scripts\python.exe" -m pip install -r python_backend/requirements.txt
if errorlevel 1 goto failed
"%~dp0.venv\Scripts\python.exe" -m python_backend.download_model --output models/bge-m3
if errorlevel 1 goto failed
echo Setup complete. Run start_bge_offline.bat, then start_dashboard.bat.
pause
exit /b 0
:failed
echo Setup failed. Check Python version, Internet access, disk space and the error above.
pause
exit /b 1
