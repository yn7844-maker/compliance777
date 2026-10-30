@echo off
setlocal
cd /d "%~dp0"
if not exist documents mkdir documents
if not exist "%~dp0.venv\Scripts\python.exe" (
 echo Run setup_bge.bat first.
 pause
 exit /b 1
)
echo Put approved UTF-8 TXT, MD, or document JSON files in the documents folder.
echo This replaces data/docs.json, including the bundled demo documents.
choice /c YN /m "Import now"
if errorlevel 2 exit /b 0
"%~dp0.venv\Scripts\python.exe" -m python_backend.prepare_documents --input documents --output data/docs.json --overwrite
if errorlevel 1 (
 echo Import failed. Check the error above. Existing corpus is kept if validation failed.
) else (
 echo Import complete. Restart start_bge_offline.bat and refresh the local dashboard.
)
pause
