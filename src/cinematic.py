"""
Cinematic post-processing pipeline.
Applies dark moody LUT + film grain + vignette + letterbox to any video.
"""
import os
import subprocess
import logging

logger = logging.getLogger(__name__)

ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")
LUT_PATH = os.path.join(ASSETS_DIR, "dark_moody_cinematic.cube")


def apply_cinematic_effects(
    input_path: str,
    output_path: str,
    lut: bool = True,
    grain: bool = True,
    vignette: bool = True,
    letterbox: bool = False,
    slow_motion: float = 1.0,
) -> str:
    """
    Apply cinematic post-processing effects to a video.

    Args:
        input_path: Path to input video
        output_path: Path to save processed video
        lut: Apply dark moody color grade
        grain: Add subtle film grain
        vignette: Darken edges
        letterbox: Add cinematic black bars (top/bottom)
        slow_motion: Speed factor (0.5 = half speed, 1.0 = normal)

    Returns:
        Path to the output video
    """
    filters = []

    # Slow motion (must come first)
    if slow_motion != 1.0:
        filters.append(f"setpts={1.0/slow_motion}*PTS")

    # Dark moody LUT color grade
    if lut and os.path.exists(LUT_PATH):
        escaped_path = LUT_PATH.replace("'", "'\\''")
        filters.append(f"lut3d='{escaped_path}'")

    # Subtle film grain
    if grain:
        filters.append("noise=c0s=6:c0f=t+u")

    # Vignette (darken edges)
    if vignette:
        filters.append("vignette=PI/4")

    # Letterbox (cinematic bars - 2.35:1 aspect within 9:16)
    if letterbox:
        filters.append("drawbox=x=0:y=0:w=iw:h=ih*0.08:color=black:t=fill")
        filters.append("drawbox=x=0:y=ih-ih*0.08:w=iw:h=ih*0.08:color=black:t=fill")

    if not filters:
        logger.info("No effects to apply, copying file")
        import shutil
        shutil.copy2(input_path, output_path)
        return output_path

    filter_chain = ",".join(filters)

    cmd = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-vf", filter_chain,
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "18",
        "-c:a", "copy",
        output_path,
    ]

    logger.info(f"Applying cinematic effects: {filter_chain}")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

    if result.returncode != 0:
        logger.error(f"FFmpeg error: {result.stderr}")
        raise RuntimeError(f"Cinematic post-processing failed: {result.stderr}")

    logger.info(f"Cinematic effects applied: {output_path}")
    return output_path


def process_moneyprinter_output(video_path: str) -> str:
    """
    Take a MoneyPrinterTurbo output video and make it cinematic.
    Overwrites the original with the processed version.
    """
    temp_path = video_path + ".tmp.mp4"

    apply_cinematic_effects(
        input_path=video_path,
        output_path=temp_path,
        lut=True,
        grain=True,
        vignette=True,
        letterbox=False,
        slow_motion=1.0,
    )

    # Replace original with processed
    os.replace(temp_path, video_path)
    logger.info(f"Replaced original with cinematic version: {video_path}")
    return video_path


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python -m src.cinematic <input.mp4> [output.mp4]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else input_file.replace(".mp4", "_cinematic.mp4")
    process_moneyprinter_output(input_file) if input_file == output_file else apply_cinematic_effects(input_file, output_file)
    print(f"Done: {output_file}")
