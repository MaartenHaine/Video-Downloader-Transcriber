#!/usr/bin/env python3
"""
Video Transcriber - Main Application Launcher
Handles command-line arguments and coordinates between downloader and transcriber
"""

import argparse
import sys
import os
import subprocess
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))


def check_dependencies():
    """Check if all required dependencies are installed"""
    required_packages = [
        'selenium',
        'yt_dlp',
        'whisper',
        'webdriver_manager',
        'faster_whisper',
        'watchdog',
        'tqdm'
    ]


    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)

    # Check FFmpeg
    try:
        subprocess.run(['ffmpeg', '-version'],
                       stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL,
                       check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("[WARNING] FFmpeg not found - required for enhanced video transcription")
        print("Install from: https://ffmpeg.org/download.html")

    if missing_packages:
        print(f"Missing required packages: {', '.join(missing_packages)}")
        print("Please run the setup script to install dependencies.")
        sys.exit(1)


def run_downloader():
    """Run the video downloader"""
    try:
        from video_downloader import FixedModernHLSDownloader

        downloader = FixedModernHLSDownloader()
        print("Starting Video Downloader...")
        print("Opening browser - use the control panel to download videos")

        portal_url = "https://toledo.kuleuven.be"
        downloader.authenticate_at_portal(portal_url)

        # Main loop - wait for user actions in panel
        while downloader.wait_for_user_action():
            pass

    except KeyboardInterrupt:
        print("\nDownloader interrupted by user")
    except Exception as e:
        print(f"Error running downloader: {e}")
    finally:
        if 'downloader' in locals():
            downloader.cleanup()


def run_transcriber():
    """Run the video transcriber"""
    try:
        from transcriber import main as transcriber_main
        print("Starting Video Transcriber...")
        transcriber_main()
    except Exception as e:
        print(f"Error running transcriber: {e}")


def run_both():
    """Run downloader then transcriber"""
    print("Starting Download and Transcribe workflow...")
    print("\nStep 1: Video Download")
    print("=" * 40)
    run_downloader()

    print("\nStep 2: Video Transcription")
    print("=" * 40)
    run_transcriber()

    print("\nWorkflow completed!")


def main():
    parser = argparse.ArgumentParser(
        description="Video Transcriber - Download and transcribe videos",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --mode download     # Download videos only
  python main.py --mode transcribe   # Transcribe existing videos
  python main.py --mode both         # Download then transcribe
        """
    )

    parser.add_argument(
        '--mode',
        choices=['download', 'transcribe', 'both'],
        required=True,
        help='Operation mode: download videos, transcribe videos, or both'
    )

    parser.add_argument(
        '--downloads-dir',
        default='downloads',
        help='Directory containing videos to transcribe (default: downloads)'
    )

    parser.add_argument(
        '--output-dir',
        default='transcriptions',
        help='Directory for transcription output (default: transcriptions)'
    )

    args = parser.parse_args()

    # Check dependencies
    check_dependencies()

    # Create directories if they don't exist
    os.makedirs(args.downloads_dir, exist_ok=True)
    os.makedirs(args.output_dir, exist_ok=True)

    # Set environment variables for transcriber
    os.environ['TRANSCRIBER_INPUT_DIR'] = args.downloads_dir
    os.environ['TRANSCRIBER_OUTPUT_DIR'] = args.output_dir

    # Run selected mode
    if args.mode == 'download':
        run_downloader()
    elif args.mode == 'transcribe':
        run_transcriber()
    elif args.mode == 'both':
        run_both()


if __name__ == "__main__":
    main()