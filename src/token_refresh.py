# src/token_refresh.py
import requests
import logging

logger = logging.getLogger(__name__)

GRAPH_API_BASE = "https://graph.facebook.com/v21.0"


def refresh_long_lived_token(current_token: str, app_id: str, app_secret: str) -> dict:
    """Exchange a valid long-lived token for a new one.

    Must be called before the current token expires (within 60 days).
    Returns dict with 'access_token' and 'expires_in'.
    """
    url = f"{GRAPH_API_BASE}/oauth/access_token"
    params = {
        "grant_type": "fb_exchange_token",
        "client_id": app_id,
        "client_secret": app_secret,
        "fb_exchange_token": current_token,
    }

    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()

    logger.info(f"Token refreshed. Expires in {data['expires_in']} seconds")
    return data


if __name__ == "__main__":
    from src.config import get_config

    config = get_config()
    result = refresh_long_lived_token(
        current_token=config["instagram_access_token"],
        app_id=config["fb_app_id"],
        app_secret=config["fb_app_secret"],
    )
    print(f"\nNew token: {result['access_token']}")
    print(f"Expires in: {result['expires_in'] // 86400} days")
    print("\nUpdate your .env file with the new token!")
