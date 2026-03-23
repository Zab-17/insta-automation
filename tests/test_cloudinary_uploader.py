# tests/test_cloudinary_uploader.py
from unittest.mock import patch, MagicMock
from src.cloudinary_uploader import upload_video


@patch("src.cloudinary_uploader.cloudinary.uploader.upload")
@patch("src.cloudinary_uploader.cloudinary.config")
def test_upload_video_returns_url(mock_config, mock_upload):
    mock_upload.return_value = {
        "secure_url": "https://res.cloudinary.com/demo/video/upload/test.mp4",
        "public_id": "test_video",
    }

    result = upload_video(
        file_path="/path/to/video.mp4",
        cloud_name="mycloud",
        api_key="key123",
        api_secret="secret123",
    )

    assert result == "https://res.cloudinary.com/demo/video/upload/test.mp4"
    mock_upload.assert_called_once()


@patch("src.cloudinary_uploader.cloudinary.uploader.upload")
@patch("src.cloudinary_uploader.cloudinary.config")
def test_upload_video_passes_resource_type_video(mock_config, mock_upload):
    mock_upload.return_value = {
        "secure_url": "https://example.com/video.mp4",
        "public_id": "test",
    }

    upload_video(
        file_path="/path/to/video.mp4",
        cloud_name="mycloud",
        api_key="key123",
        api_secret="secret123",
    )

    call_kwargs = mock_upload.call_args
    assert call_kwargs.kwargs["resource_type"] == "video"
