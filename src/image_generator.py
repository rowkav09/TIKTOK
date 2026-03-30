"""Generates images for door reveals using Flux on Replicate."""

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
        style += ", vintage aesthetic, sepia undertones, historical"
    else:
        style += ", neon glow, futuristic, sci-fi aesthetic, holographic"

    if outcome == "bad":
        style += ", eerie atmosphere, unsettling, dark moody lighting, ominous"
    else:
        style += ", warm golden light, beautiful, awe-inspiring, hopeful"

    return f"{image_prompt}, {style}"


def generate_image(image_prompt: str, door_type: str, outcome: str,
                   filename: str) -> Path:
    """Generate a single image using Flux Schnell on Replicate.

    Args:
        image_prompt: The scene description from the script generator.
        door_type: "past" or "future".
        outcome: "good" or "bad".
        filename: Output filename (without extension).

    Returns:
        Path to the saved image file.
    """
    full_prompt = _style_prompt(image_prompt, door_type, outcome)

    output = replicate.run(
        "black-forest-labs/flux-schnell",
        input={
            "prompt": full_prompt,
            "num_outputs": 1,
            "aspect_ratio": "9:16",
            "output_format": "png",
            "output_quality": 90,
        },
    )

    # Flux returns a list of FileOutput objects
    image_url = output[0]
    if hasattr(image_url, "url"):
        image_url = image_url.url
    image_url = str(image_url)

    # Download the image
    response = requests.get(image_url)
    response.raise_for_status()

    output_path = OUTPUT_DIR / f"{filename}.png"
    output_path.write_bytes(response.content)

    return output_path


def generate_door_images(script: dict, run_id: str) -> dict:
    """Generate images for both doors in a script.

    Args:
        script: The script dict from script_generator.
        run_id: Unique identifier for this video run.

    Returns:
        Dict with 'first_door' and 'second_door' image paths.
    """
    images = {}
    for door_key in ("first_door", "second_door"):
        door = script[door_key]
        path = generate_image(
            image_prompt=door["image_prompt"],
            door_type=door["type"],
            outcome=door["outcome"],
            filename=f"{run_id}_{door_key}",
        )
        images[door_key] = path
        print(f"Generated {door_key} image: {path}")

    return images


if __name__ == "__main__":
    # Test with a sample prompt
    path = generate_image(
        image_prompt="A golden ancient library filled with glowing books of infinite knowledge",
        door_type="past",
        outcome="good",
        filename="test_image",
    )
    print(f"Test image saved to: {path}")
