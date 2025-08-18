# Video Downloader & Transcriber

A comprehensive tool for downloading videos from web platforms and converting them to text transcriptions using AI-powered speech recognition. Designed for educational content, online lectures, and video documentation workflows.

## Features

### Video Download
- **Web-based Interface**: Browser control panel for easy video capture
- **Multi-platform Support**: Works with university portals and Kaltura-based systems
- **HLS Stream Support**: Downloads from modern streaming platforms
- **Queue Management**: Batch download multiple videos
- **Custom Naming**: Organize downloads with meaningful filenames

### Video Transcription
- **AI-Powered**: Uses OpenAI Whisper for high-accuracy speech recognition
- **Multiple Formats**: Generate text files, SRT subtitles, and VTT captions
- **Language Detection**: Automatic language identification
- **Batch Processing**: Transcribe multiple videos efficiently
- **Quality Options**: Choose processing speed vs. accuracy

### Workflow Integration
- **Complete Pipeline**: Download and transcribe in one operation
- **Flexible Usage**: Use components independently or together
- **Progress Tracking**: Visual feedback during long operations

## System Requirements

### Software Dependencies
- **Python 3.8 or higher**: Core runtime environment
- **Google Chrome**: Required for web automation
- **FFmpeg**: Audio/video processing (auto-installed)

### Hardware Requirements
- **RAM**: 4GB minimum, 8GB recommended for transcription
- **Storage**: 1GB free space plus video storage
- **Internet**: Stable connection for downloads

### Supported Platforms
- **Windows 10/11**
- **macOS 10.15+**
- **Linux** (Ubuntu, Debian, CentOS)

## Installation

### Quick Setup

```bash
# Clone the repository
git clone https://github.com/MaartenHaine/Video-Downloader-Transcriber.git
cd Video-Downloader-Transcriber

# Run setup (one-time installation)
# Windows:
setup.bat

# macOS/Linux:
chmod +x setup.sh
./setup.sh
