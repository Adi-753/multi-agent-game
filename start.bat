@echo off
echo Starting Multi-Agent Game Tester POC...
echo.
cd backend
echo Installing dependencies...
pip install -r requirements.txt > nul 2>&1
echo.
echo Installing Playwright browsers...
playwright install chromium > nul 2>&1
echo.
echo Starting FastAPI server...
echo Server will be available at http://localhost:8000
echo Press Ctrl+C to stop the server
echo.
python main.py
