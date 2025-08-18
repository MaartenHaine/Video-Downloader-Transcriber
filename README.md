# Video-Downloader-Transcriber

A comprehensive tool for downloading HLS video streams and converting them to text transcriptions using advanced AI. Designed specifically for educational content, lectures, and video analysis with enhanced transcription capabilities.

## Overview

This project provides two main functionalities:
- **Video Downloader**: Capture and download HLS video streams from web platforms
- **Enhanced Video Transcriber**: Convert video files to text using state-of-the-art speech recognition with multiple output formats

## Features

### Video Downloader
- **Browser-based video capture** with modern control panel
- **Automatic HLS stream detection** and download
- **Queue management** for batch downloads
- **Support for Kaltura-based platforms** (KU Leuven Toledo compatible)

## System Requirements

- **Operating System**: Windows 10+, macOS 10.14+, or Linux
- **Python**: 3.8 or higher (automatically installed if needed)
- **FFmpeg**: Required for video to audio conversion (installed automatically)
- **Chrome Browser**: Required for video capture
- **Internet Connection**: Required for downloads and initial AI model download
- **Storage**: At least 4GB free space for videos, models, and transcriptions
- **GPU** (Optional): NVIDIA GPU with CUDA for faster transcription processing

## Quick Start
This setup only needs to be done once. When the setup has been done before on the same device you can just skip to step 3.

### Step 1: Download the Project

1. Click the green "Code" button above
2. Select "Download ZIP"
3. Extract the ZIP file to your desired location

### Step 2: Run the Setup

**Windows:**
- Double-click `setup.bat`

**macOS/Linux:**
- Open Terminal in the project folder
- Run: `./setup.sh` (make executable with `chmod +x setup.sh`)

The setup script will automatically:
- Check and install Python 3.8+ if needed
- Verify FFmpeg installation (required for video transcription)
- Check Chrome browser availability
- Create virtual environment
- Install all dependencies including faster-whisper
- Set up folder structure

### Step 3: Run the Program
**Windows:**
- Double-click `run.bat` or run `setup.bat` again

**macOS/Linux:**
- Open Terminal in the project folder
- Run: `./run.sh` or `./setup.sh` again

### Step 4: Choose Your Operation

The run script will present enhanced options:
1. **Download Videos Only** - Capture videos from web platforms
2. **Transcribe Videos Only (Enhanced)** - Convert existing videos to multiple text formats
3. **Download and Transcribe** - Complete workflow from capture to text

## Installation Details

### Automatic Installation

The setup script will automatically:
- Install Python 3.8+ if not present
- Check and guide FFmpeg installation
- Create a virtual environment
- Install all required dependencies including:
  - faster-whisper (enhanced AI model)
  - watchdog (file monitoring)
  - tqdm (progress bars)
  - ffmpeg-python (video processing)
- Set up folder structure
- Configure the application

### Manual Installation

If you prefer manual setup:

```bash
# Clone or download the repository
git clone https://github.com/MaartenHaine/Video-Downloader-Transcriber.git
cd Video-Downloader-Transcriber

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Ensure FFmpeg is installed
# Windows: choco install ffmpeg
# macOS: brew install ffmpeg
# Linux: sudo apt install ffmpeg
```

## Usage Guide

### Video Download

1. Run the setup script and select "Download Videos"
2. Your browser will open with a control panel
3. Navigate to your video platform (supports Kaltura-based systems)
4. Click "Start Recording" in the panel
5. Play the video for 10+ seconds
6. Click "Stop Recording"
7. Enter a filename and add to queue
8. Process the download queue

**Supported Platforms:**
- KU Leuven Toledo Platform (Kaltura-based)
- University learning management systems
- Kaltura-based video platforms
- HLS streaming services

### Enhanced Video Transcription

#### Mode 1: Batch Processing
1. Place video files in the `downloads/` folder
2. Run setup and select "Transcribe Videos Only"
3. Choose "Batch mode" to process all existing videos
4. Select confirmation to start processing
5. Monitor real-time progress with visual progress bars
6. Find results in `output-text/` folder

#### Mode 2: File Watching (NEW)
1. Run setup and select "Transcribe Videos Only"
2. Choose "Watch mode" to monitor for new files
3. The system will automatically process any new videos added to `downloads/`
4. Perfect for continuous workflow automation

**Transcription Features:**
- **Multiple Output Formats**: 
  - `.txt` - Plain text with header
  - `.srt` - Standard subtitle format
  - `.vtt` - Web subtitle format
- **Language Detection**: Automatic detection with confidence scores
- **Progress Tracking**: Real-time progress bars per video
- **Error Recovery**: Robust error handling and recovery
- **GPU Acceleration**: Automatic CUDA detection for faster processing

### Complete Workflow

Select "Download and Transcribe" to:
1. Download videos using the browser interface
2. Automatically transcribe all downloaded videos with enhanced AI
3. Receive video files plus multiple text format outputs

## File Structure

```
Video-Downloader-Transcriber/
├── downloads/              # Downloaded videos (input for transcription)
├── output-text/           # Enhanced transcription outputs
│   ├── _cache/           # Temporary audio extraction files
│   ├── filename.txt      # Plain text transcriptions
│   ├── filename.srt      # Subtitle files
│   └── filename.vtt      # Web subtitle files
├── transcriptions/        # Legacy transcription folder (compatibility)
├── logs/                  # Application logs
├── setup.bat             # Windows setup script (enhanced)
├── setup.sh              # macOS/Linux setup script (enhanced)
├── main.py               # Main application launcher (updated)
├── video_downloader.py   # HLS video downloader
├── video_transcriber.py  # Enhanced video transcription engine
├── audio_transcriber.py  # Audio-only transcriber (reference)
├── requirements.txt      # Python dependencies (updated)
└── README.md            # This file
```

## Output Formats

### Video Downloads
- **Format**: MP4, WebM (depends on source)
- **Location**: `downloads/` folder
- **Naming**: Custom filenames as specified during download

### Enhanced Transcriptions
- **Text Files**: `.txt` format with header and clean text
- **Subtitle Files**: `.srt` format with timestamps for video players
- **Web Subtitles**: `.vtt` format for web video players
- **Location**: `output-text/` folder
- **Accuracy**: High accuracy with faster-whisper model
- **Languages**: Auto-detection with support for 90+ languages
- **Timestamps**: Precise word-level timing in subtitle formats

## Configuration Options

### Transcriber Settings (in video_transcriber.py)
```python
MODEL_SIZE = "medium"    # tiny/base/small/medium/large-v3
LANG_HINT  = "nl"        # Language hint (nl/en/auto)
USE_GPU    = True        # Enable GPU acceleration if available
```

### Supported Video Formats
- MP4, AVI, MOV, MKV, WebM, FLV, WMV, M4V, 3GP, TS

## Troubleshooting

### Common Issues

**Browser doesn't open:**
- Ensure Chrome is installed and updated
- Check firewall settings
- Try running as administrator (Windows)

**Download fails:**
- Verify internet connection
- Check university portal login status
- Ensure video is actually playing

**Transcription errors:**
- Check video has clear audio
- Verify FFmpeg is installed and in PATH
- Ensure sufficient disk space (2GB+ recommended)
- Check video format is supported

**FFmpeg not found:**
- Windows: Install with `choco install ffmpeg` or download from ffmpeg.org
- macOS: Install with `brew install ffmpeg`
- Linux: Install with `sudo apt install ffmpeg`

**Setup script fails:**
- Run as administrator/sudo
- Check Python installation (3.8+ required)
- Verify internet connection for downloads
- Ensure sufficient disk space

**GPU acceleration not working:**
- Verify NVIDIA GPU with CUDA support
- Install CUDA drivers from NVIDIA
- Set `USE_GPU = False` in video_transcriber.py for CPU-only mode

### Performance Tips

**For faster transcription:**
- Use GPU acceleration (NVIDIA CUDA)
- Use `large-v3` model for best accuracy (slower)
- Use `base` or `small` model for faster processing
- Close other applications to free RAM
- Use SSD storage for faster file access

### Getting Help

1. Check the troubleshooting section above
2. Verify all system requirements are met
3. Try running the setup script again
4. Check the console output for specific error messages
5. Ensure FFmpeg is properly installed and accessible

## Technical Details

### Enhanced Dependencies

- **Selenium**: Web browser automation
- **yt-dlp**: Video download engine
- **faster-whisper**: Enhanced speech recognition AI (replaces openai-whisper)
- **Chrome WebDriver**: Browser control
- **FFmpeg**: Video/audio processing
- **watchdog**: File system monitoring
- **tqdm**: Progress bar visualization
- **Python 3.8+**: Core runtime

### AI Model Information

- **Model**: faster-whisper 
- **Sizes**: tiny, base, small, medium, large-v3
- **Languages**: 90+ languages with auto-detection
- **GPU Support**: NVIDIA CUDA acceleration

### Security & Privacy

- **Local Processing**: All transcription happens on your computer
- **No Data Collection**: No personal data is transmitted
- **Secure Downloads**: Uses encrypted connections
- **Temporary Files**: Automatically cleaned up after processing
- **Offline Capable**: Works without internet after initial setup

## License

This project is provided as-is for educational and personal use.

### Version 1.0.0
- Initial release
- Browser-based video downloader
- Faster Whisper AI transcription
- Cross-platform setup scripts
- Queue management system

## Contributing

This is a personal project, but suggestions and improvements are welcome through GitHub issues.

---

**Note**: This tool is designed for legitimate educational use. Always respect copyright laws and institutional policies when downloading and transcribing content. The enhanced transcriber provides professional-grade accuracy suitable for academic and research purposes.
