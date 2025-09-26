Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "Starting Multi-Agent Game Tester POC Server" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Server will be available at: " -NoNewline
Write-Host "http://localhost:8000" -ForegroundColor Yellow
Write-Host "To access the UI, open your browser and go to " -NoNewline
Write-Host "http://localhost:8000" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press CTRL+C to stop the server" -ForegroundColor Red
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

& ".\venv\Scripts\Activate.ps1"
python run_server.py