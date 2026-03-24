# tests/test_instagram_api.py
from unittest.mock import patch, MagicMock
from src.instagram_api import create_media_container, publish_media, check_media_status


@patch("src.instagram_api.requests.post")
def test_create_media_container_returns_id(mock_post):
    mock_response = MagicMock()
    mock_response.json.return_value = {"id": "container_123"}
    mock_response.raise_for_status = MagicMock()
    mock_post.return_value = mock_response

    result = create_media_container(
        account_id="test_account_123",
        access_token="token123",
        video_url="https://example.com/video.mp4",
        caption="Test caption #hashtag",
    )

    assert result == "container_123"
    mock_post.assert_called_once()
    call_kwargs = mock_post.call_args
    assert "test_account_123" in call_kwargs[0][0]


@patch("src.instagram_api.requests.get")
def test_check_media_status(mock_get):
    mock_response = MagicMock()
    mock_response.json.return_value = {"status_code": "FINISHED"}
    mock_response.raise_for_status = MagicMock()
    mock_get.return_value = mock_response

    result = check_media_status(
        container_id="container_123",
        access_token="token123",
    )

    assert result == "FINISHED"


@patch("src.instagram_api.requests.post")
def test_publish_media_returns_id(mock_post):
    mock_response = MagicMock()
    mock_response.json.return_value = {"id": "media_456"}
    mock_response.raise_for_status = MagicMock()
    mock_post.return_value = mock_response

    result = publish_media(
        account_id="test_account_123",
        access_token="token123",
        container_id="container_123",
    )

    assert result == "media_456"
