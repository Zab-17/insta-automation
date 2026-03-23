# src/config.py
import os
from dotenv import load_dotenv


def get_config() -> dict:
    load_dotenv()

    required = [
        "INSTAGRAM_ACCOUNT_ID",
        "INSTAGRAM_ACCESS_TOKEN",
        "CLOUDINARY_CLOUD_NAME",
        "CLOUDINARY_API_KEY",
        "CLOUDINARY_API_SECRET",
    ]

    missing = [key for key in required if not os.getenv(key)]
    if missing:
        raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

    return {
        "instagram_account_id": os.getenv("INSTAGRAM_ACCOUNT_ID"),
        "instagram_access_token": os.getenv("INSTAGRAM_ACCESS_TOKEN"),
        "cloudinary_cloud_name": os.getenv("CLOUDINARY_CLOUD_NAME"),
        "cloudinary_api_key": os.getenv("CLOUDINARY_API_KEY"),
        "cloudinary_api_secret": os.getenv("CLOUDINARY_API_SECRET"),
        "fb_app_id": os.getenv("FB_APP_ID", ""),
        "fb_app_secret": os.getenv("FB_APP_SECRET", ""),
        "posts_per_day": int(os.getenv("POSTS_PER_DAY", "10")),
    }
