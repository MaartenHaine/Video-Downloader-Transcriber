"""
Video Transcriber
Uses OpenAI Whisper to transcribe video files to text
Reads from downloads folder by default
"""

import os
import sys
import whisper
import glob
from pathlib import Path
import time


def get_video_files(input_dir):
    """Get all video files from the input directory"""
    video_extensions = ['*.mp4', '*.avi', '*.mov', '*.mkv', '*.webm', '*.flv', '*.wmv']
    video_files = []

    for extension in video_extensions:
        pattern = os.path.join(input_dir, extension)
        video_files.extend(glob.glob(pattern))

    return sorted(video_files)


def transcribe_video(model, video_path, output_dir):
    """Transcribe a single video file"""
    print(f"\nTranscribing: {os.path.basename(video_path)}")

    try:
        # Transcribe the video
        result = model.transcribe(video_path)

        # Generate output filename
        video_name = Path(video_path).stem
        output_file = os.path.join(output_dir, f"{video_name}.txt")

        # Save transcription
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"Transcription of: {os.path.basename(video_path)}\n")
            f.write("=" * 50 + "\n\n")
            f.write(result['text'])

        print(f"✓ Saved transcription: {output_file}")
        return True

    except Exception as e:
        print(f"✗ Error transcribing {os.path.basename(video_path)}: {e}")
        return False


def main():
    """Main transcription function"""
    # Get directories from environment or use defaults
    input_dir = os.environ.get('TRANSCRIBER_INPUT_DIR', 'downloads')
    output_dir = os.environ.get('TRANSCRIBER_OUTPUT_DIR', 'transcriptions')

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    print("Video Transcriber")
    print("=" * 40)
    print(f"Input directory: {input_dir}")
    print(f"Output directory: {output_dir}")

    # Check if input directory exists
    if not os.path.exists(input_dir):
        print(f"Error: Input directory '{input_dir}' does not exist")
        print("Please make sure you have videos in the downloads folder")
        return

    # Get video files
    video_files = get_video_files(input_dir)

    if not video_files:
        print(f"No video files found in '{input_dir}'")
        print("Supported formats: MP4, AVI, MOV, MKV, WebM, FLV, WMV")
        return

    print(f"\nFound {len(video_files)} video file(s):")
    for i, video_file in enumerate(video_files, 1):
        print(f"  {i}. {os.path.basename(video_file)}")

    # Ask user for confirmation
    print(f"\nTranscriptions will be saved to: {output_dir}")
    response = input("\nProceed with transcription? (y/n): ").lower()

    if response not in ['y', 'yes']:
        print("Transcription cancelled")
        return

    # Load Whisper model
    print("\nLoading Whisper AI model...")
    try:
        model = whisper.load_model("base")  # You can change to "small", "medium", "large" for better accuracy
        print("✓ Model loaded successfully")
    except Exception as e:
        print(f"✗ Error loading model: {e}")
        return

    # Transcribe videos
    print(f"\nStarting transcription of {len(video_files)} video(s)...")
    print("This may take several minutes per video...")

    successful = 0
    failed = 0
    start_time = time.time()

    for i, video_file in enumerate(video_files, 1):
        print(f"\n[{i}/{len(video_files)}] Processing...")
        if transcribe_video(model, video_file, output_dir):
            successful += 1
        else:
            failed += 1

    # Summary
    elapsed_time = time.time() - start_time
    print(f"\n" + "=" * 50)
    print(f"Transcription completed!")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Total time: {elapsed_time:.1f} seconds")
    print(f"Output directory: {output_dir}")


if __name__ == "__main__":
    main()