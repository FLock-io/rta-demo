@echo off
REM ========================================
REM RTA Demo Installation Script
REM ========================================

echo.
echo ========================================
echo Starting RTA Demo Installation Script
echo ========================================
echo.

echo Check if .env file exists
if not exist .env (
    echo ERROR: .env file not found!
    echo Please create .env file manually
    echo.
    pause
    exit /b 1
)

echo Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)
IF EXIST venv\Scripts\activate.bat (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
) ELSE (
    echo Virtual environment not found, creating one...
    python -m venv venv
    call venv\Scripts\activate.bat
)

echo Installing dependencies from requirements.txt...
pip install -r requirements.txt
IF %ERRORLEVEL% NEQ 0 (
    echo Failed to install dependencies. Exiting.
    pause
    exit /b %ERRORLEVEL%
)

echo Starting the Streamlit app...
streamlit run Welcome.py

REM If streamlit exits, pause before closing
echo.
echo Application stopped.
pause
