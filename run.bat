@echo off
setlocal enabledelayedexpansion

REM Video Transcriber Run Script for Windows
REM Handles operation selection and running

echo ==========================================
echo         Video Transcriber
echo ==========================================
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo [ERROR] Virtual environment not found!
    echo [INFO] Please run setup.bat first to install dependencies
    pause
    exit /b 1
)

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
echo 2. Transcribe Videos Only (Enhanced)
echo    - Convert existing videos to text
echo    - Multiple formats: TXT, SRT, VTT
echo    - Progress tracking and file watching
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
    echo [INFO] Starting Enhanced Video Transcriber...
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