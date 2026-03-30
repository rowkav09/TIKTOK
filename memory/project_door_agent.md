---
name: TikTok Door Agent
description: Automated agent that generates and uploads 2 "choose a door" TikTok videos daily — past vs future theme, one good one bad
type: project
---

Automated TikTok content pipeline: "Choose a Door" concept.

- Viewers pick between a PAST door and a FUTURE door (one good, one bad, randomized)
- User provides a reusable intro video (assets/intro.mp4) showing the two doors
- Agent generates: script (Claude Haiku) → images (Flux Schnell on Replicate) → TTS (Edge TTS) → video (MoviePy/FFmpeg) → upload (TikTok Content Posting API)
- Budget target: £15/month, estimated actual cost ~£4-6/month
- Runs 2x daily via scheduler (09:00 and 19:00)

**Why:** User wants to build a low-cost automated TikTok channel around the "choose a door" viral format.

**How to apply:** All features should prioritize cost efficiency. Image generation uses Flux Schnell (cheapest). TTS uses Edge TTS (free). Keep videos short and punchy for TikTok format (9:16, ~15-20 seconds total).
