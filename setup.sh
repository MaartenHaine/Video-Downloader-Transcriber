#!/bin/bash

# Video Transcriber Setup Script with CUDA/cuDNN support
# Handles cuDNN installation for Ubuntu users

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

# Enhanced GPU and CUDA check with cuDNN installation
check_gpu_cuda() {
    print_step "Checking GPU and CUDA setup..."

    # Check NVIDIA GPU
    if command -v nvidia-smi &> /dev/null; then
        print_status "NVIDIA GPU detected"
        GPU_NAME=$(nvidia-smi --query-gpu=name --format=csv,noheader,nounits | head -1)
        print_status "GPU: $GPU_NAME"

        # Check CUDA toolkit
        if command -v nvcc &> /dev/null; then
            CUDA_VERSION=$(nvcc --version | grep "release" | sed 's/.*release \([0-9]\+\.[0-9]\+\).*/\1/')
            print_status "CUDA toolkit found: $CUDA_VERSION"

            # Check cuDNN on Linux
            if [[ "$OS" == "linux" ]]; then
                check_install_cudnn
            fi
        else
            print_warning "CUDA toolkit not found!"
            if [[ "$OS" == "linux" ]]; then
                print_status "Install with: sudo apt install nvidia-cuda-toolkit"
            fi
            print_status "GPU acceleration will be limited without CUDA toolkit"
        fi
    else
        print_warning "No NVIDIA GPU detected or drivers not installed"
        print_status "GPU acceleration will not be available"
    fi
}

# Check and install cuDNN for Linux
check_install_cudnn() {
    print_step "Checking cuDNN installation..."

    # Check if cuDNN is already installed
    if ldconfig -p | grep -q "libcudnn"; then
        print_status "cuDNN found"
        return 0
    fi

    print_warning "cuDNN not found - this is required for GPU-accelerated transcription"
    print_status "cuDNN is needed for faster-whisper GPU acceleration"

    # Ask user if they want to install cuDNN
    echo ""
    echo "Would you like to install cuDNN 9.1 for CUDA 12? (recommended for GPU acceleration)"
    echo "This requires sudo privileges and downloads ~500MB"
    read -p "Install cuDNN? (y/n): " -n 1 -r
    echo ""

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        install_cudnn
    else
        print_warning "Skipping cuDNN installation - GPU acceleration may not work"
        print_status "You can install it later by running this script again"
    fi
}

# Install cuDNN for Ubuntu
install_cudnn() {
    print_step "Installing cuDNN 9.1 for CUDA 12..."

    # Create temp directory
    TEMP_DIR=$(mktemp -d)
    cd "$TEMP_DIR"

    # Download cuDNN if not already present
    CUDNN_DEB="cudnn-local-repo-ubuntu2204-9.1.0_1.0-1_amd64.deb"
    if [[ ! -f "$HOME/Downloads/$CUDNN_DEB" ]]; then
        print_status "Downloading cuDNN installer..."
        wget -q "https://developer.download.nvidia.com/compute/cudnn/9.1.0/local_installers/$CUDNN_DEB" -O "$CUDNN_DEB"
    else
        print_status "Using existing cuDNN installer from Downloads"
        cp "$HOME/Downloads/$CUDNN_DEB" .
    fi

    # Install cuDNN
    print_status "Installing cuDNN (requires sudo)..."
    sudo dpkg -i "$CUDNN_DEB"

    # Add GPG key
    if [[ -f "/var/cudnn-local-repo-ubuntu2204-9.1.0/cudnn-*-keyring.gpg" ]]; then
        sudo cp /var/cudnn-local-repo-ubuntu2204-9.1.0/cudnn-*-keyring.gpg /usr/share/keyrings/
    fi

    # Update package list and install cuDNN packages
    sudo apt-get update
    sudo apt-get install -y libcudnn9-dev-cuda-12 libcudnn9-cuda-12

    # Cleanup
    cd - > /dev/null
    rm -rf "$TEMP_DIR"

    # Verify installation
    if ldconfig -p | grep -q "libcudnn"; then
        print_status "✓ cuDNN installed successfully"
    else
        print_warning "cuDNN installation may have failed"
    fi
}

# Check if FFmpeg is installed
check_ffmpeg() {
    print_step "Checking FFmpeg installation..."

    if command -v ffmpeg &> /dev/null; then
        print_status "FFmpeg found"
    else
        print_warning "FFmpeg not found!"
        print_status "FFmpeg is required for enhanced video transcription"
        case $OS in
            "macos")
                print_status "Install with: brew install ffmpeg"
                ;;
            "linux")
                print_status "Install with: sudo apt install ffmpeg"
                # Install FFmpeg dev libraries for Linux
                print_status "Also installing FFmpeg development libraries..."
                sudo apt install -y ffmpeg libavformat-dev libavcodec-dev libavdevice-dev libavutil-dev libavfilter-dev libswscale-dev libswresample-dev pkg-config
                ;;
            *)
                print_status "Please install from: https://ffmpeg.org/download.html"
                ;;
        esac
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

# Install dependencies with CUDA support
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

    print_status "Installing PyTorch with CUDA support..."
    pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121

    # Install other dependencies
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
    else
        print_status "Installing core dependencies..."
        pip install selenium yt-dlp openai-whisper faster-whisper webdriver-manager watchdog tqdm
    fi

    print_status "Dependencies installed successfully"

    # Test GPU setup
    print_step "Testing GPU setup..."
    python -c "
import torch
print(f'CUDA available: {torch.cuda.is_available()}')
if torch.cuda.is_available():
    print(f'CUDA version: {torch.version.cuda}')
    print(f'GPU count: {torch.cuda.device_count()}')
    print(f'GPU name: {torch.cuda.get_device_name(0)}')

    try:
        from faster_whisper import WhisperModel
        model = WhisperModel('tiny', device='cuda', compute_type='float16')
        print('✓ GPU-accelerated transcription ready!')
        del model
    except Exception as e:
        print(f'GPU acceleration test failed: {e}')
        print('Will fall back to CPU mode during transcription')
else:
    print('CUDA not available - will use CPU mode')
"
}

# Main setup function
main() {
    echo "Starting setup process..."
    echo ""

    # Run all setup steps
    check_python
    check_gpu_cuda
    check_ffmpeg
    check_chrome
    create_directories
    create_venv
    install_dependencies

    echo ""
    print_status "Setup completed successfully!"
    print_status "Use ./run.sh to start the application"
    echo ""

    if [[ "$OS" == "linux" ]] && command -v nvidia-smi &> /dev/null; then
        print_status "GPU acceleration should now work with your NVIDIA GPU!"
    fi
}

# Run main function
main