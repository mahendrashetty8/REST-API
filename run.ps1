Set-Location -Path $PSScriptRoot
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "Starting TaskFlow REST API and Web Interface..." -ForegroundColor Green
Write-Host "Open http://127.0.0.1:8000 in your browser" -ForegroundColor Yellow
Write-Host "Swagger Docs: http://127.0.0.1:8000/docs" -ForegroundColor Yellow
Write-Host "========================================================" -ForegroundColor Cyan
uvicorn app.main:app --reload
