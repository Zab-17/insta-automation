# tests/test_config.py
import os
import pytest
from unittest.mock import patch
from src.config import get_config


VALID_ENV = {
    "INSTAGRAM_ACCOUNT_ID": "123456",
    "INSTAGRAM_ACCESS_TOKEN": "token123",
    "CLOUDINARY_CLOUD_NAME": "mycloud",
    "CLOUDINARY_API_KEY": "key123",
    "CLOUDINARY_API_SECRET": "secret123",
}


@patch("src.config.load_dotenv")
def test_config_loads_instagram_account_id(mock_dotenv):
    with patch.dict(os.environ, VALID_ENV, clear=True):
        config = get_config()
        assert config["instagram_account_id"] == "123456"
        assert config["instagram_access_token"] == "token123"


@patch("src.config.load_dotenv")
def test_config_raises_if_missing_required(mock_dotenv):
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(ValueError, match="Missing required"):
            get_config()


@patch("src.config.load_dotenv")
def test_config_default_posts_per_day(mock_dotenv):
    with patch.dict(os.environ, VALID_ENV, clear=True):
        config = get_config()
        assert config["posts_per_day"] == 10
