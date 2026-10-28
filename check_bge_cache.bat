@echo off
if not defined BGE_MODEL_PATH (echo BGE_MODEL_PATH is not configured.) else (if exist "%BGE_MODEL_PATH%\config.json" (echo Local model config found. Start server and check /health.) else (echo Model config missing.))
pause
