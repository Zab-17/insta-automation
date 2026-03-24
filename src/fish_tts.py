"""
Fish Audio TTS client — generates speech using Morgan Freeman's voice.
Uses the Fish Audio API with a community Morgan Freeman voice model.
"""
import os
import requests
import logging

logger = logging.getLogger(__name__)

FISH_API_BASE = "https://api.fish.audio"
MORGAN_FREEMAN_MODEL_ID = "76bb6ae7b26c41fbbd484514fdb014c2"


def generate_speech(
    text: str,
    output_path: str,
    api_key: str,
    model_id: str = MORGAN_FREEMAN_MODEL_ID,
) -> str:
    """
    Generate speech audio using Fish Audio API.

    Args:
        text: Text to convert to speech
        output_path: Path to save the MP3/WAV file
        api_key: Fish Audio API key
        model_id: Voice model ID (default: Morgan Freeman)

    Returns:
        Path to the generated audio file
    """
    url = f"{FISH_API_BASE}/v1/tts"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "text": text,
        "reference_id": model_id,
        "format": "mp3",
        "mp3_bitrate": 128,
    }

    logger.info(f"Generating Morgan Freeman TTS ({len(text)} chars)...")
    response = requests.post(url, json=payload, headers=headers, timeout=60, stream=True)
    response.raise_for_status()

    with open(output_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    file_size = os.path.getsize(output_path)
    logger.info(f"TTS generated: {output_path} ({file_size} bytes)")
    return output_path


if __name__ == "__main__":
    import sys

    api_key = os.getenv("FISH_AUDIO_API_KEY")
    if not api_key:
        print("Set FISH_AUDIO_API_KEY environment variable")
        sys.exit(1)

    text = sys.argv[1] if len(sys.argv) > 1 else "Discipline is the bridge between goals and accomplishment."
    output = sys.argv[2] if len(sys.argv) > 2 else "/tmp/morgan_test.mp3"

    generate_speech(text, output, api_key)
    print(f"Generated: {output}")
