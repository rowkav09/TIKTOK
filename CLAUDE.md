# TikTok Door Agent

Automated "Choose a Door" TikTok video pipeline.

## Video Structure
1. `assets/intro.mp4` — intro with past door opening (~8.12s)
2. Past door slideshow (4 generated images) + TTS narration
3. `assets/midslice.mp4` — transition clip, future door opens
4. Future door slideshow (4 generated images) + TTS narration

## Key Rules
- Past door is ALWAYS revealed first, future door second
- Good/bad assignment is randomized each run
- TTS narrations must NEVER mention "doors" — describe the world only
- Bad door images should be nightmarish/horrifying (but TikTok-safe)
- 4 images per door shown as a slideshow synced to narration duration

## Pipeline
`src/pipeline.py` orchestrates: script_generator → image_generator → tts_generator → video_assembler → tiktok_uploader

## Budget
Target £15/month. Uses Flux Schnell (cheap), Edge TTS (free), Claude Haiku (cheap).

## Run
- Single video: `python run.py`
- Daily scheduler (19:00): `python scheduler.py`
