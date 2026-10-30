@echo off
cd /d "%~dp0"
if not defined BGE_MODEL_PATH set "BGE_MODEL_PATH=%~dp0models\bge-m3"
if exist "%BGE_MODEL_PATH%\config.json" (echo Local model config found. Start server and check /health.) else (echo Model missing. Run python -m python_backend.download_model --output models/bge-m3)
pause
