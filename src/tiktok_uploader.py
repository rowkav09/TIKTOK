"""Uploads videos to TikTok via the Content Posting API."""

import requests
import time
from pathlib import Path
from src.config import TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, TIKTOK_ACCESS_TOKEN

BASE_URL = "https://open.tiktokapis.com/v2"


def _init_upload(access_token: str, video_size: int) -> dict:
    """Initialize a video upload and get the upload URL."""
    response = requests.post(
        f"{BASE_URL}/post/publish/inbox/video/init/",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json; charset=UTF-8",
        },
        json={
            "source_info": {
                "source": "FILE_UPLOAD",
                "video_size": video_size,
                "chunk_size": video_size,
                "total_chunk_count": 1,
            },
        },
    )
    response.raise_for_status()
    return response.json()["data"]


def _upload_video_chunk(upload_url: str, video_path: Path,
                        video_size: int) -> None:
    """Upload the video file to TikTok's servers."""
    with open(video_path, "rb") as f:
        response = requests.put(
            upload_url,
            headers={
                "Content-Range": f"bytes 0-{video_size - 1}/{video_size}",
                "Content-Type": "video/mp4",
            },
            data=f,
        )
    response.raise_for_status()


def _publish_video(access_token: str, publish_id: str, caption: str) -> dict:
    """Publish the uploaded video with a caption."""
    response = requests.post(
        f"{BASE_URL}/post/publish/video/init/",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json; charset=UTF-8",
        },
        json={
            "post_info": {
                "title": caption,
                "privacy_level": "PUBLIC_TO_EVERYONE",
                "disable_duet": False,
                "disable_comment": False,
                "disable_stitch": False,
            },
            "source_info": {
                "source": "PULL_FROM_URL",
                "video_url": publish_id,
            },
        },
    )
    response.raise_for_status()
    return response.json()


def _check_publish_status(access_token: str, publish_id: str) -> dict:
    """Check the status of a video publish."""
    response = requests.post(
        f"{BASE_URL}/post/publish/status/fetch/",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json; charset=UTF-8",
        },
        json={"publish_id": publish_id},
    )
    response.raise_for_status()
    return response.json()


def upload_to_tiktok(video_path: Path, caption: str) -> dict:
    """Upload and publish a video to TikTok.

    Args:
        video_path: Path to the MP4 video file.
        caption: The post caption with hashtags.

    Returns:
        Dict with publish status info.
    """
    if not TIKTOK_ACCESS_TOKEN:
        print("WARNING: No TikTok access token configured.")
        print(f"Video saved locally: {video_path}")
        print(f"Caption: {caption}")
        print("Set up TikTok API credentials in .env to enable auto-upload.")
        return {"status": "skipped", "reason": "no_credentials"}

    video_size = video_path.stat().st_size

    # Step 1: Initialize upload
    print("Initializing TikTok upload...")
    init_data = _init_upload(TIKTOK_ACCESS_TOKEN, video_size)
    upload_url = init_data["upload_url"]
    publish_id = init_data["publish_id"]

    # Step 2: Upload video chunks
    print("Uploading video...")
    _upload_video_chunk(upload_url, video_path, video_size)

    # Step 3: Publish
    print("Publishing video...")
    _publish_video(TIKTOK_ACCESS_TOKEN, publish_id, caption)

    # Step 4: Check status (with retries)
    for attempt in range(5):
        time.sleep(5)
        status = _check_publish_status(TIKTOK_ACCESS_TOKEN, publish_id)
        pub_status = status.get("data", {}).get("status")
        if pub_status == "PUBLISH_COMPLETE":
            print("Video published successfully!")
            return status
        elif pub_status == "FAILED":
            print(f"Publish failed: {status}")
            return status
        print(f"Status: {pub_status}, checking again...")

    print("Publish status check timed out. Video may still be processing.")
    return status


if __name__ == "__main__":
    print("TikTok uploader module loaded.")
    print("Configure TIKTOK_ACCESS_TOKEN in .env to enable uploads.")
