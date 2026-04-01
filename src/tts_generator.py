"""Generates TTS audio using Edge TTS (free, no API key needed)."""

import asyncio
import edge_tts
from pathlib import Path
from mutagen.mp3 import MP3
from src.config import OUTPUT_DIR, TTS_VOICE


async def _generate_tts(text: str, output_path: Path, voice: str) -> Path:
    """Generate TTS audio file from text."""
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(str(output_path))
    return output_path


def get_audio_duration(audio_path: Path) -> float:
    """Get the duration of an audio file in seconds."""
    audio = MP3(str(audio_path))
    return audio.info.length


def generate_narration(text: str, filename: str,
                       voice: str = TTS_VOICE) -> tuple[Path, float]:
    """Generate TTS narration for a piece of text.

    Args:
        text: The narration text to speak.
        filename: Output filename (without extension).
        voice: Edge TTS voice name.

    Returns:
        Tuple of (path to mp3 file, duration in seconds).
    """
    output_path = OUTPUT_DIR / f"{filename}.mp3"

    asyncio.run(_generate_tts(text, output_path, voice))

    duration = get_audio_duration(output_path)
    return output_path, duration


def generate_door_narrations(script: dict,
                             run_id: str) -> dict:
    """Generate TTS for both door reveals.

    Args:
        script: The script dict from script_generator.
        run_id: Unique identifier for this video run.

    Returns:
        Dict with door keys mapping to (audio_path, duration) tuples.
    """
    narrations = {}
    for door_key in ("past_door", "future_door"):
        door = script[door_key]
        audio_path, duration = generate_narration(
            text=door["narration"],
            filename=f"{run_id}_{door_key}_narration",
        )
        narrations[door_key] = {
            "audio_path": audio_path,
            "duration": duration,
        }
        print(f"{door_key} narration: {duration:.1f}s -> {audio_path}")

    return narrations


if __name__ == "__main__":
    path, dur = generate_narration(
        "You chose the past door. Behind it, a golden library stretches "
        "into infinity. Every book contains a lifetime of wisdom.",
        "test_narration",
    )
    print(f"Audio: {path}, Duration: {dur:.1f}s")
