# src/cloudinary_uploader.py
import cloudinary
import cloudinary.uploader


def upload_video(file_path: str, cloud_name: str, api_key: str, api_secret: str) -> str:
    cloudinary.config(
        cloud_name=cloud_name,
        api_key=api_key,
        api_secret=api_secret,
    )

    result = cloudinary.uploader.upload(
        file_path,
        resource_type="video",
        folder="instagram_automation",
    )

    return result["secure_url"]
