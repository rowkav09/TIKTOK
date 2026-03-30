"""Assembles final TikTok video from intro + images + TTS audio."""

from pathlib import Path
from moviepy import (
    VideoFileClip,
    ImageClip,
    AudioFileClip,
    TextClip,
    CompositeVideoClip,
    CompositeAudioClip,
    concatenate_videoclips,
)
from src.config import OUTPUT_DIR, INTRO_VIDEO, VIDEO_WIDTH, VIDEO_HEIGHT, VIDEO_FPS


def _make_door_reveal_clip(image_path: Path, audio_path: Path,
                           duration: float, door_type: str,
                           outcome: str) -> VideoFileClip:
    """Create a clip showing a door reveal image with narration.

    The image is displayed for exactly the duration of the audio,
    with a text overlay showing which door it is.
    """
    # Load and resize image to fill 1080x1920
    img_clip = (
        ImageClip(str(image_path))
        .resized((VIDEO_WIDTH, VIDEO_HEIGHT))
        .with_duration(duration + 0.5)  # slight padding after audio ends
    )

    # Add label overlay (e.g., "THE PAST DOOR" or "THE FUTURE DOOR")
    label_text = f"THE {door_type.upper()} DOOR"
    label = (
        TextClip(
            text=label_text,
            font_size=60,
            color="white",
            font="Arial-Bold",
            stroke_color="black",
            stroke_width=3,
        )
        .with_position(("center", 120))
        .with_duration(duration + 0.5)
    )

    # Add outcome hint at the bottom
    outcome_color = "#00ff88" if outcome == "good" else "#ff4444"
    outcome_label = (
        TextClip(
            text=outcome.upper(),
            font_size=48,
            color=outcome_color,
            font="Arial-Bold",
            stroke_color="black",
            stroke_width=2,
        )
        .with_position(("center", VIDEO_HEIGHT - 200))
        .with_duration(duration + 0.5)
    )

    # Composite image + labels
    video = CompositeVideoClip(
        [img_clip, label, outcome_label],
        size=(VIDEO_WIDTH, VIDEO_HEIGHT),
    )

    # Add narration audio
    audio = AudioFileClip(str(audio_path))
    video = video.with_audio(audio)

    return video


def assemble_video(script: dict, images: dict, narrations: dict,
                   run_id: str) -> Path:
    """Assemble the full TikTok video.

    Args:
        script: The script dict with door info.
        images: Dict with 'first_door' and 'second_door' image paths.
        narrations: Dict with door keys mapping to {audio_path, duration}.
        run_id: Unique identifier for this video run.

    Returns:
        Path to the final video file.
    """
    clips = []

    # 1. Intro clip (user-provided)
    if INTRO_VIDEO.exists():
        intro = (
            VideoFileClip(str(INTRO_VIDEO))
            .resized((VIDEO_WIDTH, VIDEO_HEIGHT))
        )
        clips.append(intro)
    else:
        # If no intro video, create a simple title card
        print("WARNING: No intro video found at assets/intro.mp4")
        print("Using placeholder title card instead.")
        title = (
            TextClip(
                text="CHOOSE A DOOR\n\nPAST  or  FUTURE?",
                font_size=72,
                color="white",
                font="Arial-Bold",
                bg_color="black",
                size=(VIDEO_WIDTH, VIDEO_HEIGHT),
                text_align="center",
                vertical_align="center",
            )
            .with_duration(3)
        )
        clips.append(title)

    # 2. First door reveal
    first_door = script["first_door"]
    first_clip = _make_door_reveal_clip(
        image_path=images["first_door"],
        audio_path=narrations["first_door"]["audio_path"],
        duration=narrations["first_door"]["duration"],
        door_type=first_door["type"],
        outcome=first_door["outcome"],
    )
    clips.append(first_clip)

    # 3. Second door reveal
    second_door = script["second_door"]
    second_clip = _make_door_reveal_clip(
        image_path=images["second_door"],
        audio_path=narrations["second_door"]["audio_path"],
        duration=narrations["second_door"]["duration"],
        door_type=second_door["type"],
        outcome=second_door["outcome"],
    )
    clips.append(second_clip)

    # Concatenate all clips
    final = concatenate_videoclips(clips, method="compose")
    final = final.with_fps(VIDEO_FPS)

    # Export
    output_path = OUTPUT_DIR / f"{run_id}_final.mp4"
    final.write_videofile(
        str(output_path),
        codec="libx264",
        audio_codec="aac",
        fps=VIDEO_FPS,
        preset="medium",
        threads=4,
    )

    # Clean up
    for clip in clips:
        clip.close()
    final.close()

    print(f"Final video: {output_path}")
    return output_path


if __name__ == "__main__":
    print("Video assembler module loaded. Use assemble_video() to create videos.")
