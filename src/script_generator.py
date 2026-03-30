"""Generates scripts for door reveal videos using Claude Haiku."""

import json
import random
from anthropic import Anthropic
from src.config import ANTHROPIC_API_KEY

client = Anthropic(api_key=ANTHROPIC_API_KEY)

SYSTEM_PROMPT = """You are a scriptwriter for a viral TikTok series called "Choose a Door".

The format: viewers see two doors — a PAST door and a FUTURE door. One door is GOOD, one is BAD.
After the intro, each door is revealed one at a time with a dramatic narration.

Your job is to write:
1. A short, punchy narration for the FIRST door reveal (2-3 sentences, ~5-8 seconds when spoken)
2. A short, punchy narration for the SECOND door reveal (2-3 sentences, ~5-8 seconds when spoken)
3. An image prompt for each door's reveal scene

Rules:
- The GOOD door should describe something amazing, aspirational, or beautiful
- The BAD door should describe something eerie, unsettling, dystopian, or creepy (but NOT graphic violence or gore — keep it TikTok-safe)
- Past-themed doors should feel vintage, historical, nostalgic, or ancient
- Future-themed doors should feel sci-fi, futuristic, advanced, or otherworldly
- Narrations should be dramatic and engaging — like a narrator in a thriller
- Image prompts should be vivid and detailed for AI image generation
- Keep narrations SHORT — this is TikTok, attention spans are tiny

Respond in this exact JSON format:
{
  "first_door": {
    "type": "past" or "future",
    "outcome": "good" or "bad",
    "narration": "The narration text spoken during this reveal",
    "image_prompt": "Detailed image generation prompt for this scene"
  },
  "second_door": {
    "type": "past" or "future",
    "outcome": "good" or "bad",
    "narration": "The narration text spoken during this reveal",
    "image_prompt": "Detailed image generation prompt for this scene"
  },
  "caption": "A TikTok caption with hashtags (under 150 chars)"
}"""


def generate_script() -> dict:
    """Generate a randomized door reveal script.

    Returns a dict with first_door, second_door, and caption.
    """
    # Randomly assign good/bad to past/future
    past_is_good = random.choice([True, False])
    # Randomly decide which door is revealed first
    first_is_past = random.choice([True, False])

    if first_is_past:
        first_type = "past"
        first_outcome = "good" if past_is_good else "bad"
        second_type = "future"
        second_outcome = "bad" if past_is_good else "good"
    else:
        first_type = "future"
        first_outcome = "bad" if past_is_good else "good"
        second_type = "past"
        second_outcome = "good" if past_is_good else "bad"

    user_prompt = (
        f"Generate a door reveal script.\n"
        f"First door: {first_type} door — {first_outcome} outcome.\n"
        f"Second door: {second_type} door — {second_outcome} outcome.\n"
        f"Make it unique and creative. Surprise the viewer."
    )

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    )

    text = response.content[0].text

    # Parse JSON from response (handle markdown code blocks)
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0]
    elif "```" in text:
        text = text.split("```")[1].split("```")[0]

    script = json.loads(text.strip())

    # Validate structure
    for key in ("first_door", "second_door", "caption"):
        if key not in script:
            raise ValueError(f"Missing key in script: {key}")
    for door_key in ("first_door", "second_door"):
        door = script[door_key]
        for field in ("type", "outcome", "narration", "image_prompt"):
            if field not in door:
                raise ValueError(f"Missing field '{field}' in {door_key}")

    return script


if __name__ == "__main__":
    script = generate_script()
    print(json.dumps(script, indent=2))
