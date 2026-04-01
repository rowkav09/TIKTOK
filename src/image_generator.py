"""Generates images for door reveals using Flux on Replicate."""

import time
import requests
import replicate
from pathlib import Path
from src.config import REPLICATE_API_TOKEN, OUTPUT_DIR

# Set token for replicate client
import os
os.environ["REPLICATE_API_TOKEN"] = REPLICATE_API_TOKEN or ""


def _style_prompt(image_prompt: str, door_type: str, outcome: str) -> str:
    """Enhance the raw prompt with consistent styling."""
    style = (
        "cinematic, dramatic lighting, highly detailed, 4k, "
        "vertical composition 9:16 aspect ratio, "
        "vibrant colors, movie poster quality"
    )
    if door_type == "past":
        style += ", fantasy art, mythological, ancient civilization, painterly"
    else:
        style += ", neon glow, futuristic, sci-fi aesthetic, holographic, cybernetic"

    if outcome == "bad":
        style += (
            ", nightmarish, deeply unsettling, psychological horror, "
            "dark oppressive atmosphere, dread, decay, ominous shadows, "
            "distorted reality, surreal horror"
        )
    else:
        style += ", warm golden light, beautiful, awe-inspiring, hopeful, majestic"

    return f"{image_prompt}, {style}"


def generate_image(image_prompt: str, door_type: str, outcome: str,
                   filename: str, retries: int = 3) -> Path:
    """Generate a single image using Flux 1.1 Pro on Replicate.

    Returns:
        Path to the saved image file.
    """
    full_prompt = _style_prompt(image_prompt, door_type, outcome)

    for attempt in range(retries):
        try:
            output = replicate.run(
                "black-forest-labs/flux-1.1-pro",
                input={
                    "prompt": full_prompt,
                    "num_outputs": 1,
                    "aspect_ratio": "9:16",
                    "output_format": "png",
                    "output_quality": 90,
                },
            )

            # Flux may return a list or a single FileOutput depending on model
            if isinstance(output, list):
                image_url = output[0]
            else:
                image_url = output
            if hasattr(image_url, "url"):
                image_url = image_url.url
            image_url = str(image_url)

            # Download the image
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()

            output_path = OUTPUT_DIR / f"{filename}.png"
            output_path.write_bytes(response.content)
            return output_path

        except Exception as e:
            if attempt < retries - 1:
                wait = 15 * (attempt + 1)
                print(f"    Retry {attempt+1}/{retries} after error: {e}")
                time.sleep(wait)
            else:
                raise


def generate_door_images(script: dict, run_id: str) -> dict:
    """Generate images for both doors in a script.

    Each door has multiple image prompts, so this generates
    IMAGES_PER_DOOR images per door.

    Returns:
        Dict with 'past_door' and 'future_door' keys, each mapping
        to a list of image Paths.
    """
    images = {}
    door_types = {"past_door": "past", "future_door": "future"}

    for door_key, door_type in door_types.items():
        door = script[door_key]
        door_images = []
        for i, prompt in enumerate(door["image_prompts"]):
            if i > 0 or door_key != "past_door":
                time.sleep(12)  # respect rate limits
            path = generate_image(
                image_prompt=prompt,
                door_type=door_type,
                outcome=door["outcome"],
                filename=f"{run_id}_{door_key}_{i}",
            )
            door_images.append(path)
            print(f"  Generated {door_key} image {i+1}/{len(door['image_prompts'])}: {path}")
        images[door_key] = door_images

    return images


if __name__ == "__main__":
    path = generate_image(
        image_prompt="A golden ancient library filled with glowing books of infinite knowledge",
        door_type="past",
        outcome="good",
        filename="test_image",
    )
    print(f"Test image saved to: {path}")
