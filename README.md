# Video-Downloader-Transcriber-

A comprehensive tool for downloading HLS video streams and converting them to text transcriptions. Designed for educational content, lectures, and video analysis.

## Overview

This project provides two main functionalities:
- **Video Downloader**: Capture and download HLS video streams from web platforms
- **Video Transcriber**: Convert video files to text using advanced speech recognition

## Features

- **Browser-based video capture** with modern control panel
- **Automatic HLS stream detection** and download
- **Queue management** for batch downloads
- **Advanced speech recognition** using Whisper AI
- **Cross-platform support** (Windows, macOS, Linux)
- **User-friendly setup** with automated installation

## System Requirements

- **Operating System**: Windows 10+, macOS 10.14+, or Linux
- **Python**: 3.8 or higher (automatically installed if needed)
- **Chrome Browser**: Required for video capture
- **Internet Connection**: Required for downloads and AI processing
- **Storage**: At least 2GB free space for videos and models

## Quick Start

### Step 1: Download the Project

1. Click the green "Code" button above
2. Select "Download ZIP"
3. Extract the ZIP file to your desired location

### Step 2: Run the Setup

**Windows:**
- Double-click `setup.bat`

**macOS/Linux:**
- Open Terminal in the project folder
- Run: `./setup.sh` (`chmod +x setup.sh`)

### Step 3: Choose Your Operation

The setup script will present three options:
1. **Download Videos Only** - Capture videos from web platforms
2. **Transcribe Videos Only** - Convert existing videos to text
3. **Download and Transcribe** - Complete workflow from capture to text

## Installation Details

### Automatic Installation

The setup script will automatically:
- Install Python 3.8+ if not present
- Create a virtual environment
- Install all required dependencies
- Set up folder structure
- Configure the application

### Manual Installation

If you prefer manual setup:

```bash
# Clone or download the repository
git clone https://github.com/MaartenHaine/transcripter-video.git
cd transcripter-video

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
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
- University learning management systems
- Kaltura-based video platforms
- HLS streaming services

### Video Transcription

1. Place video files in the `downloads` folder
2. Run the setup script and select "Transcribe Videos"
3. Choose your transcription options:
   - Language detection
   - Output format (txt, srt, vtt)
   - Processing quality
4. Wait for processing to complete

### Complete Workflow

Select "Download and Transcribe" to:
1. Download videos using the browser interface
2. Automatically transcribe all downloaded videos
3. Receive both video files and text transcriptions

## File Structure

```
transcripter-video/
├── downloads/              # Downloaded videos
├── transcriptions/         # Generated text files
├── setup.bat              # Windows setup script
├── setup.sh               # macOS/Linux setup script
├── main.py                # Main application launcher
├── video_downloader.py    # HLS video downloader
├── transcriber.py         # Video transcription engine
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Output Formats

### Video Downloads
- **Format**: MP4, WebM (depends on source)
- **Location**: `downloads/` folder
- **Naming**: Custom filenames as specified during download

### Transcriptions
- **Text Files**: `.txt` format with timestamps
- **Subtitle Files**: `.srt` and `.vtt` formats available
- **Location**: `transcriptions/` folder
- **Accuracy**: Varies based on audio quality and language

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
- Verify file format is supported
- Ensure sufficient disk space

**Setup script fails:**
- Run as administrator/sudo
- Check Python installation
- Verify internet connection for downloads

### Getting Help

1. Check the troubleshooting section above
2. Verify all system requirements are met
3. Try running the setup script again
4. Check the console output for specific error messages

## Technical Details

### Dependencies

- **Selenium**: Web browser automation
- **yt-dlp**: Video download engine
- **OpenAI Whisper**: Speech recognition AI
- **Chrome WebDriver**: Browser control
- **Python 3.8+**: Core runtime

### Security & Privacy

- **Local Processing**: All transcription happens on your computer
- **No Data Collection**: No personal data is transmitted
- **Secure Downloads**: Uses encrypted connections
- **Temporary Files**: Automatically cleaned up

## License

This project is provided as-is for educational and personal use.

## Changelog

### Version 1.0.0
- Initial release
- Browser-based video downloader
- Whisper AI transcription
- Cross-platform setup scripts
- Queue management system

## Contributing

This is a personal project, but suggestions and improvements are welcome through GitHub issues.

---

**Note**: This tool is designed for legitimate educational use. Always respect copyright laws and institutional policies when downloading and transcribing content.
