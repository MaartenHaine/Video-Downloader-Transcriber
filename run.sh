#!/bin/bash

# Video Transcriber Run Script
# Handles operation selection and running

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

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

echo "=========================================="
echo "        Video Transcriber"
echo "=========================================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    print_error "Virtual environment not found!"
    print_status "Please run ./setup.sh first to install dependencies"
    exit 1
fi

# Detect operating system for activation
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
    ACTIVATE_CMD="source venv/Scripts/activate"
else
    ACTIVATE_CMD="source venv/bin/activate"
fi

# Run the selected operation
run_operation() {
    local choice=$1

    # Activate virtual environment
    eval $ACTIVATE_CMD

    case $choice in
        1)
            print_status "Starting Video Downloader..."
            python main.py --mode download
            ;;
        2)
            print_status "Starting Enhanced Video Transcriber..."
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

# Main loop
while true; do
    echo "=========================================="
    echo "        Choose Your Operation"
    echo "=========================================="
    echo ""
    echo "1. Download Videos Only"
    echo "   - Capture videos from web platforms"
    echo "   - Save to downloads/ folder"
    echo ""
    echo "2. Transcribe Videos Only (Enhanced)"
    echo "   - Convert existing videos to text"
    echo "   - Multiple formats: TXT, SRT, VTT"
    echo "   - Progress tracking and file watching"
    echo ""
    echo "3. Download and Transcribe"
    echo "   - Complete workflow"
    echo "   - Download then automatically transcribe"
    echo ""
    echo "4. Exit"
    echo ""
    read -p "Enter your choice (1-4): " choice

    if run_operation $choice; then
        break
    fi
    echo ""
done