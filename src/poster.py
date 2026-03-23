# src/poster.py
import os
import shutil
import time
import logging

from src.cloudinary_uploader import upload_video
from src.instagram_api import create_media_container, check_media_status, publish_media

logger = logging.getLogger(__name__)

VIDEO_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv"}


def find_pending_posts(pending_dir: str) -> list[dict]:
    posts = []

    if not os.path.exists(pending_dir):
        return posts

    for folder_name in sorted(os.listdir(pending_dir)):
        folder_path = os.path.join(pending_dir, folder_name)
        if not os.path.isdir(folder_path):
            continue

        caption_path = os.path.join(folder_path, "caption.txt")
        if not os.path.exists(caption_path):
            logger.warning(f"Skipping {folder_name}: no caption.txt")
            continue

        video_path = None
        for file in os.listdir(folder_path):
            ext = os.path.splitext(file)[1].lower()
            if ext in VIDEO_EXTENSIONS:
                video_path = os.path.join(folder_path, file)
                break

        if not video_path:
            logger.warning(f"Skipping {folder_name}: no video file")
            continue

        with open(caption_path, "r") as f:
            caption = f.read().strip()

        posts.append({
            "folder_path": folder_path,
            "folder_name": folder_name,
            "video_path": video_path,
            "caption": caption,
        })

    return posts


def move_to_posted(folder_path: str, posted_dir: str) -> None:
    folder_name = os.path.basename(folder_path)
    dest = os.path.join(posted_dir, folder_name)
    shutil.move(folder_path, dest)
    logger.info(f"Moved {folder_name} to posted/")


def post_content(post: dict, config: dict) -> str:
    logger.info(f"Uploading video: {post['folder_name']}")
    video_url = upload_video(
        file_path=post["video_path"],
        cloud_name=config["cloudinary_cloud_name"],
        api_key=config["cloudinary_api_key"],
        api_secret=config["cloudinary_api_secret"],
    )
    logger.info(f"Video uploaded: {video_url}")

    logger.info("Creating media container...")
    container_id = create_media_container(
        account_id=config["instagram_account_id"],
        access_token=config["instagram_access_token"],
        video_url=video_url,
        caption=post["caption"],
    )

    logger.info("Waiting for Instagram to process video...")
    for attempt in range(30):
        status = check_media_status(container_id, config["instagram_access_token"])
        if status == "FINISHED":
            break
        if status == "ERROR":
            raise RuntimeError(f"Instagram failed to process video: {post['folder_name']}")
        time.sleep(10)
    else:
        raise TimeoutError(f"Video processing timed out: {post['folder_name']}")

    logger.info("Publishing...")
    media_id = publish_media(
        account_id=config["instagram_account_id"],
        access_token=config["instagram_access_token"],
        container_id=container_id,
    )
    logger.info(f"Published! Media ID: {media_id}")

    return media_id
