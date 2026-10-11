@echo off
cd /d "%~dp0"
echo ========================================================
echo Starting TaskFlow REST API and Web Interface...
echo Open http://127.0.0.1:8000 in your browser
echo Swagger Docs: http://127.0.0.1:8000/docs
echo ========================================================
uvicorn app.main:app --reload
pause
