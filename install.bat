@echo off
REM ========================================
REM RTA Demo Installation & Run Script
REM ========================================

echo.
echo ========================================
echo Starting RTA Demo Installation Script
echo ========================================
echo.

REM ========================================
REM 1. Configuration & Environment Variables
REM ========================================

REM =====================================================
REM SET YOUR API CREDENTIALS HERE:
REM =====================================================
set "OPENAI_API_KEY="
set "OPENAI_BASE_URL="
REM =====================================================

set REPO_URL=https://github.com/FLock-io/rta-demo.git
set TARGET_BRANCH=feat/add-windows-bat
set REPO_DIR_NAME=rta-demo

REM ========================================
REM 2. Repo Setup & Git Update Logic
REM ========================================
echo Checking for Git...
git --version >nul 2>&1
if %errorlevel% equ 0 goto GIT_CHECK_DONE

echo Git is not installed or not in PATH.
where winget >nul 2>&1
if %errorlevel% neq 0 goto GIT_MANUAL_FAIL

    echo Attempting to install Git via Winget...
    winget install --id Git.Git -e --source winget --accept-source-agreements --accept-package-agreements --override "/VERYSILENT /NORESTART"
    if %errorlevel% neq 0 goto GIT_INSTALL_FAIL
    
    echo Git installed successfully.
echo Refreshening environment variables...
set "PATH=%PATH%;C:\Program Files\Git\cmd"
goto GIT_CHECK_DONE

:GIT_MANUAL_FAIL
echo ERROR: Winget package manager not found. Cannot install Git automatically.
goto GIT_FAIL_MSG

:GIT_INSTALL_FAIL
echo ERROR: Failed to install Git automatically.

:GIT_FAIL_MSG
echo Please install Git manually from https://git-scm.com/downloads
pause
exit /b 1

:GIT_CHECK_DONE
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo WARNING: Git was installed but is not yet recognized in the current session.
    echo Please close this window and run the script again.
    pause
    exit /b 1
)

echo (Git LFS will ONLY download GTFS data files - this may take a moment on first run)
echo (TTSS Route Summary data will be downloaded from Intranet by the application)

REM Check if we are already inside the repo (look for Welcome.py)
if exist "Welcome.py" (
    echo Running from inside the repository...
    set "PROJECT_ROOT=."
) else (
    REM Check if the repo folder exists in current directory
    if exist "%REPO_DIR_NAME%" (
        echo Found existing %REPO_DIR_NAME% folder...
        cd "%REPO_DIR_NAME%"
        set "PROJECT_ROOT=."
    ) else (
        echo Repository not found. Cloning from GitHub...
        echo URL: %REPO_URL%
        echo Branch: %TARGET_BRANCH%
        
        git clone -b %TARGET_BRANCH% %REPO_URL%
        if %errorlevel% neq 0 (
            echo ERROR: Failed to clone repository.
            pause
            exit /b 1
        )
        cd "%REPO_DIR_NAME%"
        set "PROJECT_ROOT=."
    )
)

REM Now inside the repo, perform updates
echo.
echo Checking for updates on branch %TARGET_BRANCH%...

REM Ensure we are on the correct branch
git checkout %TARGET_BRANCH% 2>nul
if %errorlevel% neq 0 (
    echo Switching to branch %TARGET_BRANCH%...
    git fetch origin %TARGET_BRANCH%
    git checkout -b %TARGET_BRANCH% origin/%TARGET_BRANCH%
)

REM Pull latest changes
echo Pulling latest changes...
git pull origin %TARGET_BRANCH%

REM Explicitly pull only GTFS data via LFS
echo Ensuring GTFS data is available...
git lfs install >nul 2>&1
git lfs pull --include="Talk_to_your_Data/Ops_GTFS_29-Aug-2025/**" --exclude=""

if %errorlevel% equ 0 (
    echo Successfully updated to latest version.
) else (
    echo WARNING: Failed to pull latest changes. Proceeding with local version.
)

REM ========================================
REM 3. Python Environment Setup
REM ========================================
echo.
echo Checking Python installation...
python --version >nul 2>&1
if %errorlevel% equ 0 goto PYTHON_CHECK_DONE

echo Python is not installed or not in PATH.
where winget >nul 2>&1
if %errorlevel% neq 0 goto PYTHON_MANUAL_FAIL

    echo Attempting to install Python 3.12 via Winget...
    winget install --id Python.Python.3.12 -e --source winget --accept-source-agreements --accept-package-agreements --override "/quiet PrependPath=1"
    if %errorlevel% neq 0 goto PYTHON_INSTALL_FAIL
    
    echo Python installed successfully.
echo You may need to restart this script for the new PATH to take effect.
goto PYTHON_CHECK_DONE

:PYTHON_MANUAL_FAIL
echo ERROR: Winget package manager not found. Cannot install Python automatically.
goto PYTHON_FAIL_MSG

:PYTHON_INSTALL_FAIL
echo ERROR: Failed to install Python automatically.

:PYTHON_FAIL_MSG
echo Please install Python 3.8+ from https://www.python.org/downloads/
echo Make sure to check "Add Python to PATH" during installation
pause
exit /b 1

:PYTHON_CHECK_DONE
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo WARNING: Python was installed but is not yet recognized in the current session.
    echo Please close this window and run the script again.
    pause
    exit /b 1
)

REM Check for existing venv
IF EXIST venv\Scripts\activate.bat (
    echo Activating existing virtual environment...
    call venv\Scripts\activate.bat
) ELSE (
    echo Virtual environment not found. Creating new one...
    python -m venv venv
    call venv\Scripts\activate.bat
)

REM ========================================
REM 4. Dependency Management
REM ========================================
echo.
echo Installing/Updating dependencies from requirements.txt...
pip install -r requirements.txt
IF %ERRORLEVEL% NEQ 0 (
    echo Failed to install dependencies. Exiting.
    pause
    exit /b %ERRORLEVEL%
)

REM ========================================
REM 5. Run Application
REM ========================================
echo.
echo Starting the Streamlit app...
streamlit run Welcome.py

REM If streamlit exits, pause before closing
echo.
echo Application stopped.
pause
