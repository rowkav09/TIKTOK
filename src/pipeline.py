"""Main pipeline — orchestrates the full video creation and upload flow."""

import sys
import uuid
import os
from datetime import datetime

# Fix Windows console encoding for emoji/unicode
if sys.platform == "win32":
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from src.script_generator import generate_script
from src.image_generator import generate_door_images
from src.tts_generator import generate_door_narrations
from src.video_assembler import assemble_video
from src.tiktok_uploader import upload_to_tiktok


def run_pipeline() -> dict:
    """Run the full pipeline: script → images → TTS → video → upload.

    Returns:
        Dict with run metadata and results.
    """
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S") + "_" + uuid.uuid4().hex[:6]
    print(f"=== Starting pipeline run: {run_id} ===\n")

    # Step 1: Generate script
    print("[1/5] Generating script...")
    script = generate_script()
    print(f"  Past door: {script['past_door']['outcome']}")
    print(f"  Future door: {script['future_door']['outcome']}")
    print(f"  Caption: {script['caption']}\n")

    # Step 2: Generate images (multiple per door)
    print("[2/5] Generating images...")
    images = generate_door_images(script, run_id)
    print()

    # Step 3: Generate TTS narrations
    print("[3/5] Generating narrations...")
    narrations = generate_door_narrations(script, run_id)
    print()

    # Step 4: Assemble video
    print("[4/5] Assembling video...")
    video_path = assemble_video(script, images, narrations, run_id)
    print()

    # Step 5: Upload to TikTok
    print("[5/5] Uploading to TikTok...")
    upload_result = upload_to_tiktok(video_path, script["caption"])
    print()

    print(f"=== Pipeline complete: {run_id} ===")
    return {
        "run_id": run_id,
        "script": script,
        "video_path": str(video_path),
        "upload_result": upload_result,
    }


def main():
    try:
        result = run_pipeline()
        print(f"\nVideo saved to: {result['video_path']}")
    except Exception as e:
        print(f"\nPipeline failed: {e}", file=sys.stderr)
        raise


if __name__ == "__main__":
    main()
