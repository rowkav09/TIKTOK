---
name: TikTok Door Agent
description: Automated agent that generates and uploads 1 "choose a door" TikTok video daily — past vs future theme, one good one bad
type: project
---

Automated TikTok content pipeline: "Choose a Door" concept.

- Viewers pick between a PAST door and a FUTURE door (one good, one bad, randomized)
- Past door ALWAYS opens first, future door second
- User provides two video assets:
  - `assets/intro.mp4` (~8.12s) — shows the two doors, past door opens
  - `assets/midslice.mp4` — transition clip saying "door 2 - the future" with future door opening
- Video structure: intro → past door images + TTS → midslice → future door images + TTS
- Agent generates: script (Claude Haiku) → 4 images per door (Flux Schnell on Replicate) → TTS (Edge TTS) → video (MoviePy/FFmpeg) → upload (TikTok Content Posting API)
- TTS narrations NEVER mention "doors" — only describe the world/scene content
- Bad door images are nightmarish/horrifying (TikTok-safe), good door images are beautiful/majestic
- Budget target: £15/month, estimated actual cost ~£4-6/month
- Runs 1x daily via scheduler (19:00)

**Why:** User wants to build a low-cost automated TikTok channel around the "choose a door" viral format.

**How to apply:** All features should prioritize cost efficiency. Image generation uses Flux Schnell (cheapest). TTS uses Edge TTS (free). Multiple images per door keep viewers entertained as a slideshow synced to narration audio.
