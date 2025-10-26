@echo off
:: --- Secure Portal Launcher ---
echo Setting up Secure Portal environment...
SETLOCAL

:: Create venv if it doesn’t exist
IF NOT EXIST "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

:: Activate venv
CALL venv\Scripts\activate

:: Install required packages
echo Installing dependencies...
pip install --upgrade pip >nul
pip install -r requirements.txt >nul

:: Launch the Flask app
echo Starting Secure Portal...
start "" http://127.0.0.1:5000
python app.py

ENDLOCAL
pause
