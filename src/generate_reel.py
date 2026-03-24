"""
Master reel generation pipeline.

Flow:
1. Fish Audio generates Morgan Freeman voiceover
2. MoneyPrinterTurbo assembles video (stock footage + voiceover + subtitles + music)
3. Cinematic post-processing (dark LUT + grain + vignette)
4. Output saved to content/pending/ for Instagram posting
"""
import os
import sys
import time
import json
import shutil
import logging
import requests

from src.fish_tts import generate_speech
from src.cinematic import apply_cinematic_effects

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

MONEYPRINTER_API = "http://127.0.0.1:8080/api/v1"
PENDING_DIR = "content/pending"


def generate_reel(
    subject: str,
    script: str,
    search_terms: list[str],
    caption: str,
    fish_api_key: str,
    voice_model: str = "76bb6ae7b26c41fbbd484514fdb014c2",
    cinematic: bool = True,
) -> str:
    """
    Generate a complete Instagram reel.

    Args:
        subject: Video topic/title
        script: Narration script
        search_terms: Keywords for stock footage search
        caption: Instagram caption text
        fish_api_key: Fish Audio API key
        voice_model: Fish Audio voice model ID
        cinematic: Apply cinematic post-processing

    Returns:
        Path to the pending post folder
    """
    # Create post folder
    folder_name = subject.lower().replace(" ", "-")[:50]
    post_dir = os.path.join(PENDING_DIR, folder_name)
    os.makedirs(post_dir, exist_ok=True)

    # Step 1: Generate Morgan Freeman voiceover
    logger.info("Step 1: Generating voiceover with Fish Audio...")
    audio_path = os.path.join(post_dir, "voiceover.mp3")
    generate_speech(
        text=script,
        output_path=audio_path,
        api_key=fish_api_key,
        model_id=voice_model,
    )

    # Step 2: Send to MoneyPrinterTurbo with custom audio
    logger.info("Step 2: Generating video with MoneyPrinterTurbo...")
    payload = {
        "video_subject": subject,
        "video_script": script,
        "video_terms": search_terms,
        "video_aspect": "9:16",
        "custom_audio_file": os.path.abspath(audio_path),
        "subtitle_enabled": True,
        "subtitle_position": "bottom",
        "font_size": 60,
        "text_fore_color": "#FFFFFF",
        "stroke_color": "#000000",
        "stroke_width": 1.5,
        "bgm_type": "random",
        "bgm_volume": 0.15,
        "video_count": 1,
        "video_clip_duration": 3,
    }

    response = requests.post(
        f"{MONEYPRINTER_API}/videos",
        json=payload,
        timeout=30,
    )
    response.raise_for_status()
    task_id = response.json()["data"]["task_id"]
    logger.info(f"MoneyPrinterTurbo task: {task_id}")

    # Poll until complete
    for attempt in range(60):  # 10 minutes max
        time.sleep(10)
        status = requests.get(f"{MONEYPRINTER_API}/tasks/{task_id}").json()
        state = status["data"]["state"]
        progress = status["data"]["progress"]
        logger.info(f"Progress: {progress}% (state: {state})")

        if state == 1:  # Complete
            video_url = status["data"]["videos"][0]
            break
        elif state == -1:  # Failed
            raise RuntimeError(f"MoneyPrinterTurbo failed: {json.dumps(status, indent=2)}")
    else:
        raise TimeoutError("MoneyPrinterTurbo timed out after 10 minutes")

    # Download the video
    video_path = os.path.join(post_dir, "video.mp4")
    video_file_path = video_url.replace(
        "http://127.0.0.1:8080/tasks/",
        os.path.expanduser("~/Desktop/MoneyPrinterTurbo/storage/tasks/"),
    )
    shutil.copy2(video_file_path, video_path)
    logger.info(f"Video saved: {video_path}")

    # Step 3: Apply cinematic post-processing
    if cinematic:
        logger.info("Step 3: Applying cinematic effects...")
        temp_path = video_path + ".tmp.mp4"
        apply_cinematic_effects(
            input_path=video_path,
            output_path=temp_path,
            lut=True,
            grain=True,
            vignette=True,
        )
        os.replace(temp_path, video_path)
        logger.info("Cinematic effects applied!")

    # Step 4: Save caption
    caption_path = os.path.join(post_dir, "caption.txt")
    with open(caption_path, "w") as f:
        f.write(caption)

    logger.info(f"Reel ready at: {post_dir}")
    logger.info("Run 'python main.py --once' to post it to Instagram!")
    return post_dir


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    fish_key = os.getenv("FISH_AUDIO_API_KEY")
    if not fish_key:
        print("Add FISH_AUDIO_API_KEY to your .env file")
        sys.exit(1)

    # Example usage
    generate_reel(
        subject="Discipline Creates Freedom",
        script="Time does not wait. Neither should you. While they sleep, you build. While they doubt, you execute. Silence the noise. Stay disciplined. Discipline creates freedom. Stay relentless.",
        search_terms=["luxury watch", "city skyline sunrise", "man suit lobby", "gym training", "luxury car driving", "person working laptop dark", "rooftop city night", "confident walk"],
        caption="Discipline creates freedom. Stay relentless. 🔥\n\n#discipline #motivation #success #mindset #grindset #luxurylifestyle #entrepreneur",
        fish_api_key=fish_key,
    )
