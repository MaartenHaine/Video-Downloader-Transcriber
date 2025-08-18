#!/bin/bash

# Video Transcriber Setup Script
# Cross-platform setup for Windows (via Git Bash), macOS, and Linux

set -e

echo "=========================================="
echo "    Video Transcriber Setup Script"
echo "=========================================="
echo ""

# Color codes for better output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Detect operating system
detect_os() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "linux"
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        echo "windows"
    else
        echo "unknown"
    fi
}

OS=$(detect_os)
print_status "Detected operating system: $OS"

# Check if Python is installed
check_python() {
    print_step "Checking Python installation..."

    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
    else
        print_error "Python is not installed!"
        print_status "Please install Python 3.8+ from https://python.org"
        exit 1
    fi

    # Check Python version
    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | cut -d' ' -f2)
    print_status "Found Python $PYTHON_VERSION"

    # Check if version is 3.8+
    if $PYTHON_CMD -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)" 2>/dev/null; then
        print_status "Python version is compatible"
    else
        print_error "Python 3.8 or higher is required"
        print_status "Please upgrade Python from https://python.org"
        exit 1
    fi
}

# Check if Chrome is installed
check_chrome() {
    print_step "Checking Chrome browser..."

    case $OS in
        "macos")
            if [ -d "/Applications/Google Chrome.app" ]; then
                print_status "Chrome found"
            else
                print_warning "Chrome not found. Please install from https://chrome.google.com"
            fi
            ;;
        "linux")
            if command -v google-chrome &> /dev/null || command -v chromium-browser &> /dev/null; then
                print_status "Chrome/Chromium found"
            else
                print_warning "Chrome not found. Please install: sudo apt install google-chrome-stable"
            fi
            ;;
        "windows")
            if [ -f "/c/Program Files/Google/Chrome/Application/chrome.exe" ] || [ -f "/c/Program Files (x86)/Google/Chrome/Application/chrome.exe" ]; then
                print_status "Chrome found"
            else
                print_warning "Chrome not found. Please install from https://chrome.google.com"
            fi
            ;;
    esac
}

# Create directory structure
create_directories() {
    print_step "Creating directory structure..."

    mkdir -p downloads
    mkdir -p transcriptions
    mkdir -p logs

    print_status "Created directories: downloads/, transcriptions/, logs/"
}

# Create virtual environment
create_venv() {
    print_step "Creating virtual environment..."

    if [ -d "venv" ]; then
        print_warning "Virtual environment already exists, removing old one..."
        rm -rf venv
    fi

    $PYTHON_CMD -m venv venv
    print_status "Virtual environment created"
}

# Activate virtual environment and install dependencies
install_dependencies() {
    print_step "Installing dependencies..."

    # Activate virtual environment
    case $OS in
        "windows")
            source venv/Scripts/activate
            ;;
        *)
            source venv/bin/activate
            ;;
    esac

    # Upgrade pip
    python -m pip install --upgrade pip

    # Install dependencies
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
    else
        print_status "Installing core dependencies..."
        pip install selenium yt-dlp openai-whisper webdriver-manager
    fi

    print_status "Dependencies installed successfully"
}

# Show menu and get user choice
show_menu() {
    echo ""
    echo "=========================================="
    echo "        Choose Your Operation"
    echo "=========================================="
    echo ""
    echo "1. Download Videos Only"
    echo "   - Capture videos from web platforms"
    echo "   - Save to downloads/ folder"
    echo ""
    echo "2. Transcribe Videos Only"
    echo "   - Convert existing videos to text"
    echo "   - Process files from downloads/ folder"
    echo ""
    echo "3. Download and Transcribe"
    echo "   - Complete workflow"
    echo "   - Download then automatically transcribe"
    echo ""
    echo "4. Exit"
    echo ""
    read -p "Enter your choice (1-4): " choice
    echo $choice
}

# Run the selected operation
run_operation() {
    local choice=$1

    # Activate virtual environment
    case $OS in
        "windows")
            source venv/Scripts/activate
            ;;
        *)
            source venv/bin/activate
            ;;
    esac

    case $choice in
        1)
            print_status "Starting Video Downloader..."
            python main.py --mode download
            ;;
        2)
            print_status "Starting Video Transcriber..."
            python main.py --mode transcribe
            ;;
        3)
            print_status "Starting Download and Transcribe workflow..."
            python main.py --mode both
            ;;
        4)
            print_status "Exiting..."
            exit 0
            ;;
        *)
            print_error "Invalid choice. Please select 1-4."
            return 1
            ;;
    esac
}

# Main setup function
main() {
    echo "Starting setup process..."
    echo ""

    # Run all setup steps
    check_python
    check_chrome
    create_directories
    create_venv
    install_dependencies

    echo ""
    print_status "Setup completed successfully!"
    echo ""

    # Show menu and handle user choice
    while true; do
        choice=$(show_menu)
        if run_operation $choice; then
            break
        fi
        echo ""
    done
}

# Run main function
main