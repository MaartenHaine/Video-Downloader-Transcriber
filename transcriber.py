"""
Video Transcriber
Enhanced version using faster-whisper to transcribe video files to text
Reads from downloads folder by default
"""

import os
import sys
import time
import threading
import subprocess
import json
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from faster_whisper import WhisperModel
from tqdm import tqdm

# Make sure required folders exist
os.makedirs("downloads", exist_ok=True)
os.makedirs("transcriptions", exist_ok=True)

# ----- Config -----
CACHE_DIR = Path("transcriptions") / "_cache"

MODEL_SIZE = "medium"  # tiny/base/small/medium/large-v3
LANG_HINT = "nl"  # hint voor Nederlands; None = autodetect
USE_GPU = True  # False als je geen NVIDIA GPU hebt
COMPUTE_TYPE = "float16" if USE_GPU else "int8"

# Video extensions (expanded from your original)
VIDEO_EXTS = {".mp4", ".avi", ".mov", ".mkv", ".webm", ".flv", ".wmv", ".m4v", ".3gp", ".ts"}

# ---- Progress helpers ----
PROG_LOCK = threading.Lock()
PROG_NEXT_POS = 0


# ------ Helpers ------
def is_file_stable(path: Path, wait_seconds=2):
    """Wacht tot bestand niet meer groeit (klaar met kopiëren/export)."""
    last_size = -1
    while True:
        try:
            size = path.stat().st_size
            if size == last_size:
                return True
            last_size = size
            time.sleep(wait_seconds)
        except FileNotFoundError:
            return False


def extract_audio_from_video(input_path: Path) -> Path:
    """
    Extracteer audio naar wav (16kHz mono) voor video bestanden.
    """
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    out_wav = CACHE_DIR / (input_path.stem + "_audio.wav")

    # Skip extraction if audio file already exists
    if out_wav.exists():
        return out_wav

    cmd = [
        "ffmpeg", "-y", "-i", str(input_path),
        "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1",
        str(out_wav)
    ]

    try:
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        return out_wav
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] FFmpeg failed for {input_path.name}: {e}")
        raise


def get_video_duration_seconds(path: Path) -> float | None:
    """Meet de duur via ffprobe; return None als het niet lukt."""
    try:
        cmd = [
            "ffprobe", "-v", "error", "-print_format", "json",
            "-show_format", "-show_streams", str(path)
        ]
        out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL)
        info = json.loads(out.decode("utf-8", errors="ignore"))
        if "format" in info and "duration" in info["format"]:
            return float(info["format"]["duration"])
        for st in info.get("streams", []):
            if "duration" in st:
                return float(st["duration"])
    except Exception:
        pass
    return None


def get_video_files(input_dir):
    """Get all video files from the input directory"""
    video_files = []
    input_path = Path(input_dir)

    if not input_path.exists():
        return video_files

    for ext in VIDEO_EXTS:
        video_files.extend(input_path.glob(f"*{ext}"))
        video_files.extend(input_path.glob(f"*{ext.upper()}"))

    return sorted(video_files)


# ------ Original transcribe_video function enhanced ------
def transcribe_video(model: WhisperModel, video_path, output_dir):
    """Transcribe a single video file with enhanced features"""
    input_path = Path(video_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    base = output_dir / input_path.stem

    # Skip if output already exists
    if (base.with_suffix(".txt").exists() and
            base.with_suffix(".srt").exists() and
            base.with_suffix(".vtt").exists()):
        print(f"[SKIP] Transcriptie bestaat al: {input_path.name}")
        return True

    print(f"Transcribing: {input_path.name}")

    try:
        # Extract audio from video
        audio_path = extract_audio_from_video(input_path)

        # --- Voortgangsbalk ---
        total_seconds = get_video_duration_seconds(input_path)
        with PROG_LOCK:
            global PROG_NEXT_POS
            pos = PROG_NEXT_POS
            PROG_NEXT_POS += 1

        bar = tqdm(total=total_seconds if total_seconds else 0,
                   unit="s", position=pos, leave=False,
                   dynamic_ncols=True,
                   desc=input_path.name)

        try:
            segments, info = model.transcribe(
                str(audio_path),
                vad_filter=True,
                beam_size=5,
                language=LANG_HINT,
                task="transcribe"
            )
            print(f"[INFO] Detected language: {info.language} (prob={info.language_probability:.2f})")

            segs = []
            last_shown = 0.0
            for s in segments:
                segs.append(s)
                if total_seconds:
                    inc = max(0.0, float(s.end) - last_shown)
                    last_shown = float(s.end)
                    bar.update(inc)

            if not total_seconds and segs:
                last_end = float(segs[-1].end)
                bar.total = last_end
                bar.update(max(0.0, bar.total - bar.n))

            # Write TXT file (original format)
            txt_path = base.with_suffix(".txt")
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(f"Transcription of: {input_path.name}\n")
                f.write("=" * 50 + "\n\n")
                for s in segs:
                    f.write(s.text.strip() + "\n")

            # SRT format function
            def fmt_ts_srt(t):
                h = int(t // 3600)
                m = int((t % 3600) // 60)
                s = int(t % 60)
                ms = int((t - int(t)) * 1000)
                return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

            srt_path = base.with_suffix(".srt")
            with open(srt_path, "w", encoding="utf-8") as f:
                for i, s in enumerate(segs, start=1):
                    f.write(f"{i}\n{fmt_ts_srt(s.start)} --> {fmt_ts_srt(s.end)}\n{s.text.strip()}\n\n")

            # VTT format function
            def fmt_ts_vtt(t):
                h = int(t // 3600)
                m = int((t % 3600) // 60)
                s = int(t % 60)
                ms = int((t - int(t)) * 1000)
                return f"{h:02d}:{m:02d}:{s:02d}.{ms:03d}"

            vtt_path = base.with_suffix(".vtt")
            with open(vtt_path, "w", encoding="utf-8") as f:
                f.write("WEBVTT\n\n")
                for s in segs:
                    f.write(f"{fmt_ts_vtt(s.start)} --> {fmt_ts_vtt(s.end)}\n{s.text.strip()}\n\n")

            print(f"✓ Saved transcriptions: {txt_path.name}, {srt_path.name}, {vtt_path.name}")
            return True

        finally:
            bar.close()
            # Clean up temporary audio file
            if audio_path.exists() and audio_path.parent == CACHE_DIR:
                try:
                    audio_path.unlink()
                except Exception:
                    pass

    except Exception as e:
        print(f"✗ Error transcribing {input_path.name}: {e}")
        return False


# ------ Watcher voor real-time processing ------
class VideoHandler(FileSystemEventHandler):
    def __init__(self, model):
        self.model = model

    def on_created(self, event):
        if event.is_directory:
            return
        path = Path(event.src_path)
        if path.suffix.lower() not in VIDEO_EXTS:
            return
        if is_file_stable(path):
            output_dir = os.environ.get('TRANSCRIBER_OUTPUT_DIR', 'transcriptions')
            threading.Thread(target=transcribe_video, args=(self.model, path, output_dir), daemon=True).start()


def run_batch_mode(model):
    """Process all existing video files in downloads folder"""
    input_dir = os.environ.get('TRANSCRIBER_INPUT_DIR', 'downloads')
    output_dir = os.environ.get('TRANSCRIBER_OUTPUT_DIR', 'transcriptions')

    print("Video Transcriber - Enhanced Batch Mode")
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
        print(f"Supported formats: {', '.join(sorted(VIDEO_EXTS))}")
        return

    print(f"\nFound {len(video_files)} video file(s):")
    for i, video_file in enumerate(video_files, 1):
        print(f"  {i}. {video_file.name}")

    # Ask user for confirmation
    print(f"\nTranscriptions will be saved to: {output_dir}")
    response = input("\nProceed with transcription? (y/n): ").lower()

    if response not in ['y', 'yes']:
        print("Transcription cancelled")
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


def run_watch_mode(model):
    """Watch downloads folder for new video files"""
    input_dir = os.environ.get('TRANSCRIBER_INPUT_DIR', 'downloads')

    print("Video Transcriber - Watch Mode")
    print("=" * 40)
    print(f"[READY] Watching for video files in: {Path(input_dir).resolve()}")

    observer = Observer()
    observer.schedule(VideoHandler(model), str(input_dir), recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[INFO] Stopping file watcher...")
        observer.stop()
    observer.join()


def main():
    """Main transcription function with enhanced features"""
    # Get directories from environment or use defaults (keeping original behavior)
    input_dir = os.environ.get('TRANSCRIBER_INPUT_DIR', 'downloads')
    output_dir = os.environ.get('TRANSCRIBER_OUTPUT_DIR', 'transcriptions')

    # Create directories
    os.makedirs(input_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    # Initialize Whisper model
    print("Loading Enhanced Whisper AI model...")
    try:
        device = "cuda" if USE_GPU else "cpu"
        model = WhisperModel(MODEL_SIZE, device=device, compute_type=COMPUTE_TYPE)

        try:
            d = getattr(model, "device", device)
        except Exception:
            d = device
        print(f"✓ Model loaded successfully")
        print(f"[DEBUG] Model device: {d} | compute_type: {COMPUTE_TYPE}")
    except Exception as e:
        print(f"✗ Error loading model: {e}")
        print("Falling back to basic mode...")
        # Fallback to original whisper if faster-whisper fails
        try:
            import whisper
            model = whisper.load_model("base")
            print("✓ Fallback model loaded successfully")

            # Simple transcription for fallback
            video_files = get_video_files(input_dir)
            if not video_files:
                print(f"No video files found in '{input_dir}'")
                return

            for video_file in video_files:
                result = model.transcribe(str(video_file))
                output_file = os.path.join(output_dir, f"{video_file.stem}.txt")
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(f"Transcription of: {video_file.name}\n")
                    f.write("=" * 50 + "\n\n")
                    f.write(result['text'])
                print(f"✓ Saved transcription: {output_file}")
            return
        except Exception as e2:
            print(f"✗ Fallback also failed: {e2}")
            return

    # Mode selection
    print("\nSelect mode:")
    print("1. Batch mode - Process all existing videos in downloads folder")
    print("2. Watch mode - Monitor downloads folder for new videos")

    while True:
        try:
            choice = input("\nEnter your choice (1 or 2): ").strip()
            if choice == "1":
                run_batch_mode(model)
                break
            elif choice == "2":
                run_watch_mode(model)
                break
            else:
                print("Please enter 1 or 2")
        except KeyboardInterrupt:
            print("\nExiting...")
            break


if __name__ == "__main__":
    main()