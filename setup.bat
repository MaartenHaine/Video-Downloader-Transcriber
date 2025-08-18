@echo off
setlocal enabledelayedexpansion

REM Video Transcriber Setup Script for Windows
REM Provides user-friendly setup and operation selection

echo ==========================================
echo     Video Transcriber Setup Script
echo ==========================================
echo.

REM Check if Python is installed
echo [STEP] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed!
    echo [INFO] Please install Python 3.8+ from https://python.org
    echo [INFO] Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

REM Get Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [INFO] Found Python %PYTHON_VERSION%

REM Check Python version (basic check for 3.x)
python -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)" >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python 3.8 or higher is required
    echo [INFO] Please upgrade Python from https://python.org
    pause
    exit /b 1
)
echo [INFO] Python version is compatible

REM Check if Chrome is installed
echo [STEP] Checking Chrome browser...
if exist "C:\Program Files\Google\Chrome\Application\chrome.exe" (
    echo [INFO] Chrome found
) else if exist "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" (
    echo [INFO] Chrome found
) else (
    echo [WARNING] Chrome not found. Please install from https://chrome.google.com
)

REM Create directory structure
echo [STEP] Creating directory structure...
if not exist "downloads" mkdir downloads
if not exist "transcriptions" mkdir transcriptions
if not exist "logs" mkdir logs
echo [INFO] Created directories: downloads\, transcriptions\, logs\

REM Create virtual environment
echo [STEP] Creating virtual environment...
if exist "venv" (
    echo [WARNING] Virtual environment already exists, removing old one...
    rmdir /s /q venv
)
python -m venv venv
echo [INFO] Virtual environment created

REM Activate virtual environment and install dependencies
echo [STEP] Installing dependencies...
call venv\Scripts\activate

REM Upgrade pip
python -m pip install --upgrade pip

REM Install dependencies
if exist "requirements.txt" (
    pip install -r requirements.txt
) else (
    echo [INFO] Installing core dependencies...
    pip install selenium yt-dlp openai-whisper webdriver-manager
)
echo [INFO] Dependencies installed successfully

echo.
echo [INFO] Setup completed successfully!
echo.

REM Main menu loop
:menu
echo ==========================================
echo         Choose Your Operation
echo ==========================================
echo.
echo 1. Download Videos Only
echo    - Capture videos from web platforms
echo    - Save to downloads\ folder
echo.
echo 2. Transcribe Videos Only
echo    - Convert existing videos to text
echo    - Process files from downloads\ folder
echo.
echo 3. Download and Transcribe
echo    - Complete workflow
echo    - Download then automatically transcribe
echo.
echo 4. Exit
echo.
set /p choice=Enter your choice (1-4):

REM Activate virtual environment for operations
call venv\Scripts\activate

if "%choice%"=="1" (
    echo [INFO] Starting Video Downloader...
    python main.py --mode download
    goto end
) else if "%choice%"=="2" (
    echo [INFO] Starting Video Transcriber...
    python main.py --mode transcribe
    goto end
) else if "%choice%"=="3" (
    echo [INFO] Starting Download and Transcribe workflow...
    python main.py --mode both
    goto end
) else if "%choice%"=="4" (
    echo [INFO] Exiting...
    goto end
) else (
    echo [ERROR] Invalid choice. Please select 1-4.
    echo.
    goto menu
)

:end
pause