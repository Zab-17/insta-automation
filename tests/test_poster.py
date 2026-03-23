# tests/test_poster.py
import os
import pytest
import shutil
import tempfile
from unittest.mock import patch, MagicMock
from src.poster import find_pending_posts, post_content, move_to_posted


class TestFindPendingPosts:
    def test_finds_folders_with_video_and_caption(self, tmp_path):
        post_dir = tmp_path / "post1"
        post_dir.mkdir()
        (post_dir / "video.mp4").write_text("fake video")
        (post_dir / "caption.txt").write_text("My caption")

        results = find_pending_posts(str(tmp_path))
        assert len(results) == 1
        assert results[0]["caption"] == "My caption"
        assert results[0]["video_path"].endswith("video.mp4")

    def test_skips_folders_without_caption(self, tmp_path):
        post_dir = tmp_path / "post1"
        post_dir.mkdir()
        (post_dir / "video.mp4").write_text("fake video")

        results = find_pending_posts(str(tmp_path))
        assert len(results) == 0

    def test_finds_mp4_and_mov_files(self, tmp_path):
        post_dir = tmp_path / "post1"
        post_dir.mkdir()
        (post_dir / "reel.mov").write_text("fake video")
        (post_dir / "caption.txt").write_text("My caption")

        results = find_pending_posts(str(tmp_path))
        assert len(results) == 1


class TestPostContent:
    @patch("src.poster.publish_media", return_value="media_789")
    @patch("src.poster.check_media_status", return_value="FINISHED")
    @patch("src.poster.create_media_container", return_value="container_123")
    @patch("src.poster.upload_video", return_value="https://example.com/video.mp4")
    def test_post_content_returns_media_id(self, mock_upload, mock_create, mock_status, mock_publish):
        post = {
            "folder_path": "/tmp/post1",
            "folder_name": "post1",
            "video_path": "/tmp/post1/video.mp4",
            "caption": "Test caption",
        }
        config = {
            "cloudinary_cloud_name": "cloud",
            "cloudinary_api_key": "key",
            "cloudinary_api_secret": "secret",
            "instagram_account_id": "123",
            "instagram_access_token": "token",
        }

        result = post_content(post, config)
        assert result == "media_789"
        mock_upload.assert_called_once()
        mock_create.assert_called_once()
        mock_publish.assert_called_once()

    @patch("src.poster.check_media_status", return_value="ERROR")
    @patch("src.poster.create_media_container", return_value="container_123")
    @patch("src.poster.upload_video", return_value="https://example.com/video.mp4")
    def test_post_content_raises_on_processing_error(self, mock_upload, mock_create, mock_status):
        post = {
            "folder_path": "/tmp/post1",
            "folder_name": "post1",
            "video_path": "/tmp/post1/video.mp4",
            "caption": "Test",
        }
        config = {
            "cloudinary_cloud_name": "cloud",
            "cloudinary_api_key": "key",
            "cloudinary_api_secret": "secret",
            "instagram_account_id": "123",
            "instagram_access_token": "token",
        }

        with pytest.raises(RuntimeError, match="failed to process"):
            post_content(post, config)


class TestMoveToPosted:
    def test_moves_folder(self, tmp_path):
        pending = tmp_path / "pending"
        posted = tmp_path / "posted"
        pending.mkdir()
        posted.mkdir()

        post_dir = pending / "post1"
        post_dir.mkdir()
        (post_dir / "video.mp4").write_text("fake")

        move_to_posted(str(post_dir), str(posted))

        assert not post_dir.exists()
        assert (posted / "post1").exists()
