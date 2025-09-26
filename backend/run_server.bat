@echo off
echo ==================================================
echo Starting Multi-Agent Game Tester POC Server
echo ==================================================
echo.
echo Server will be available at: http://localhost:8000
echo To access the UI, open your browser and go to http://localhost:8000
echo.
echo Press CTRL+C to stop the server
echo ==================================================
echo.

call venv\Scripts\activate
python run_server.py
pause