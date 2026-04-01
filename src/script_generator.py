"""Generates scripts for door reveal videos using Claude Haiku."""

import json
import random
from anthropic import Anthropic
from src.config import ANTHROPIC_API_KEY, IMAGES_PER_DOOR

client = Anthropic(api_key=ANTHROPIC_API_KEY)

SYSTEM_PROMPT = f"""You are a scriptwriter for a viral TikTok series called "Choose a Door".

The format: viewers see two doors — a PAST door and a FUTURE door. One is GOOD, one is BAD.
The past door is ALWAYS revealed first, then the future door.

Your job is to write:
1. A narration for the PAST door reveal (3-5 sentences, ~8-12 seconds when spoken)
2. A narration for the FUTURE door reveal (3-5 sentences, ~8-12 seconds when spoken)
3. {IMAGES_PER_DOOR} distinct image prompts per door — each showing a different angle or scene from that world

CRITICAL RULES:
- NEVER mention "doors" anywhere in the narrations. Describe only the world/scene itself.
  BAD: "Behind this door lies a golden city..."
  GOOD: "A golden city stretches across the horizon..."
- The GOOD world should be breathtaking, beautiful, aspirational, fantastical
- The BAD world should be deeply unsettling, eerie, nightmarish, borderline horrifying (but NO real gore, graphic violence, or anything that violates TikTok guidelines — think psychological horror, dystopian decay, surreal dread)
- Past worlds should feel ancient, mythological, fantastical, like stepping into a legend
- Future worlds should feel sci-fi, advanced, otherworldly, alien
- Narrations should be dramatic and immersive — paint the scene with words
- Each image prompt must depict a DIFFERENT scene/angle of the same world so viewers see variety
- Image prompts should be vivid and highly detailed for AI image generation
- All {IMAGES_PER_DOOR} images for one door must share the same coherent theme and visual style

Respond in this exact JSON format:
{{
  "past_door": {{
    "outcome": "good" or "bad",
    "narration": "The narration text for the past world (NO mention of doors)",
    "image_prompts": [
      "Image prompt 1 — a wide establishing shot of this world",
      "Image prompt 2 — a closer detail or different area",
      "Image prompt 3 — a final dramatic perspective"
    ]
  }},
  "future_door": {{
    "outcome": "good" or "bad",
    "narration": "The narration text for the future world (NO mention of doors)",
    "image_prompts": [
      "Image prompt 1 — a wide establishing shot of this world",
      "Image prompt 2 — a closer detail or different area",
      "Image prompt 3 — a final dramatic perspective"
    ]
  }},
  "caption": "A TikTok caption with hashtags (under 150 chars)"
}}"""


def generate_script() -> dict:
    """Generate a door reveal script.

    Past door is always first. Good/bad assignment is random.

    Returns a dict with past_door, future_door, and caption.
    """
    past_is_good = random.choice([True, False])

    past_outcome = "good" if past_is_good else "bad"
    future_outcome = "bad" if past_is_good else "good"

    user_prompt = (
        f"Generate a door reveal script.\n"
        f"Past door: {past_outcome} outcome.\n"
        f"Future door: {future_outcome} outcome.\n"
        f"Make it unique, creative, and immersive. "
        f"The {past_outcome if past_outcome == 'bad' else future_outcome} world "
        f"should be genuinely unsettling and nightmarish. "
        f"Remember: NEVER mention doors in the narrations."
    )

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=2048,
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
    for key in ("past_door", "future_door", "caption"):
        if key not in script:
            raise ValueError(f"Missing key in script: {key}")
    for door_key in ("past_door", "future_door"):
        door = script[door_key]
        for field in ("outcome", "narration", "image_prompts"):
            if field not in door:
                raise ValueError(f"Missing field '{field}' in {door_key}")
        if len(door["image_prompts"]) < IMAGES_PER_DOOR:
            raise ValueError(
                f"{door_key} has {len(door['image_prompts'])} image prompts, "
                f"expected {IMAGES_PER_DOOR}"
            )

    return script


if __name__ == "__main__":
    script = generate_script()
    print(json.dumps(script, indent=2))
