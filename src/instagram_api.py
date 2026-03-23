# src/instagram_api.py
import requests

GRAPH_API_BASE = "https://graph.facebook.com/v21.0"


def create_media_container(
    account_id: str,
    access_token: str,
    video_url: str,
    caption: str,
    media_type: str = "REELS",
) -> str:
    url = f"{GRAPH_API_BASE}/{account_id}/media"
    params = {
        "video_url": video_url,
        "caption": caption,
        "media_type": media_type,
        "access_token": access_token,
    }

    response = requests.post(url, params=params)
    response.raise_for_status()
    return response.json()["id"]


def check_media_status(container_id: str, access_token: str) -> str:
    url = f"{GRAPH_API_BASE}/{container_id}"
    params = {
        "fields": "status_code",
        "access_token": access_token,
    }

    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()["status_code"]


def publish_media(account_id: str, access_token: str, container_id: str) -> str:
    url = f"{GRAPH_API_BASE}/{account_id}/media_publish"
    params = {
        "creation_id": container_id,
        "access_token": access_token,
    }

    response = requests.post(url, params=params)
    response.raise_for_status()
    return response.json()["id"]
