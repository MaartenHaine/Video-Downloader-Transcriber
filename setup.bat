@echo off
setlocal enabledelayedexpansion

REM Video Transcriber Setup Script for Windows
REM Only handles installation and setup

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

REM Check if FFmpeg is installed
echo [STEP] Checking FFmpeg installation...
ffmpeg -version >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] FFmpeg not found!
    echo [INFO] FFmpeg is required for enhanced video transcription
    echo [INFO] Please install from: https://ffmpeg.org/download.html
    echo [INFO] Or use chocolatey: choco install ffmpeg
    echo [INFO] Make sure FFmpeg is added to your PATH
    pause
) else (
    echo [INFO] FFmpeg found
)

REM Check if Chrome is installed
echo [STEP] Checking Chrome browser...
if exist "C:\Program Files\Google\Chrome\Application\chrome.exe" (
    echo [INFO] Chrome found
) else if exist "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" (
    echo [INFO] Chrome found
) else (
    echo [WARNING] Chrome not found. Please install from https://chrome.google.com
)

REM Check for NVIDIA GPU (optional)
echo [STEP] Checking for NVIDIA GPU...
nvidia-smi >nul 2>&1
if %errorlevel% equ 0 (
    echo [INFO] NVIDIA GPU detected - GPU acceleration will be available
) else (
    echo [INFO] No NVIDIA GPU detected - will use CPU mode
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

REM Install PyTorch with CUDA support first
echo [INFO] Installing PyTorch with CUDA support...
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121

REM Install other dependencies
if exist "requirements.txt" (
    pip install -r requirements.txt
) else (
    echo [INFO] Installing core dependencies...
    pip install selenium yt-dlp openai-whisper faster-whisper webdriver-manager watchdog tqdm librosa soundfile
)

REM Test CUDA setup
echo [STEP] Testing GPU setup...
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}'); print(f'GPU name: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"N/A\"}')"

echo [INFO] Dependencies installed successfully
echo.
echo [INFO] Setup completed successfully!
echo [INFO] Use run.bat to start the application
echo.
pause