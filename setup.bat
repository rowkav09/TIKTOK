@echo off
echo === TikTok Door Agent Setup ===
echo.

echo [1/3] Creating virtual environment...
python -m venv .venv
call .venv\Scripts\activate

echo [2/3] Installing dependencies...
pip install -r requirements.txt

echo [3/3] Creating .env from template...
if not exist .env (
    copy .env.example .env
    echo Created .env — fill in your API keys!
) else (
    echo .env already exists, skipping.
)

echo.
echo === Setup complete! ===
echo.
echo Next steps:
echo   1. Edit .env with your API keys
echo   2. Place your intro video at assets\intro.mp4
echo   3. Run: python run.py (single video)
echo   4. Run: python scheduler.py (2x daily)
