"""Assembles final TikTok video from intro + images + TTS audio + midslice."""

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
from src.config import (
    OUTPUT_DIR, INTRO_VIDEO, MIDSLICE_VIDEO,
    VIDEO_WIDTH, VIDEO_HEIGHT, VIDEO_FPS,
)


def _make_slideshow_clip(image_paths: list[Path], audio_path: Path,
                         duration: float) -> CompositeVideoClip:
    """Create a slideshow of images synced to a narration audio track.

    Images are shown sequentially, each for an equal share of the total duration.
    """
    num_images = len(image_paths)
    time_per_image = (duration + 0.5) / num_images  # +0.5s padding after audio

    clips = []
    for i, img_path in enumerate(image_paths):
        img_clip = (
            ImageClip(str(img_path))
            .resized((VIDEO_WIDTH, VIDEO_HEIGHT))
            .with_duration(time_per_image)
            .with_start(i * time_per_image)
        )
        clips.append(img_clip)

    total_duration = num_images * time_per_image
    video = CompositeVideoClip(clips, size=(VIDEO_WIDTH, VIDEO_HEIGHT))
    video = video.with_duration(total_duration)

    # Add narration audio
    audio = AudioFileClip(str(audio_path))
    video = video.with_audio(audio)

    return video


def assemble_video(script: dict, images: dict, narrations: dict,
                   run_id: str) -> Path:
    """Assemble the full TikTok video.

    Structure:
        1. intro.mp4 (past door opens)
        2. Past door slideshow + narration
        3. midslice.mp4 (transition to future door)
        4. Future door slideshow + narration

    Args:
        script: The script dict with past_door and future_door info.
        images: Dict with 'past_door' and 'future_door' lists of image paths.
        narrations: Dict with door keys mapping to {audio_path, duration}.
        run_id: Unique identifier for this video run.

    Returns:
        Path to the final video file.
    """
    clips = []

    # 1. Intro clip
    if INTRO_VIDEO.exists():
        intro = (
            VideoFileClip(str(INTRO_VIDEO))
            .resized((VIDEO_WIDTH, VIDEO_HEIGHT))
        )
        clips.append(intro)
    else:
        print("WARNING: No intro video found at assets/intro.mp4")
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

    # 2. Past door slideshow
    past_clip = _make_slideshow_clip(
        image_paths=images["past_door"],
        audio_path=narrations["past_door"]["audio_path"],
        duration=narrations["past_door"]["duration"],
    )
    clips.append(past_clip)

    # 3. Midslice transition clip
    if MIDSLICE_VIDEO.exists():
        midslice = (
            VideoFileClip(str(MIDSLICE_VIDEO))
            .resized((VIDEO_WIDTH, VIDEO_HEIGHT))
        )
        clips.append(midslice)
    else:
        print("WARNING: No midslice video found at assets/midslice.mp4")

    # 4. Future door slideshow
    future_clip = _make_slideshow_clip(
        image_paths=images["future_door"],
        audio_path=narrations["future_door"]["audio_path"],
        duration=narrations["future_door"]["duration"],
    )
    clips.append(future_clip)

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
