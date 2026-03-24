# Instagram Automation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Python automation that watches a folder for video content, uploads it to Cloudinary, and publishes it to Instagram via the Graph API with scheduled posting.

**Architecture:** A Python script monitors a `content/pending/` folder. Each subfolder contains a video file and a `caption.txt`. The script uploads the video to Cloudinary to get a public URL, creates an Instagram media container, waits for processing, publishes it, then moves the subfolder to `content/posted/`. A scheduler spaces posts throughout the day.

**Tech Stack:** Python 3, `requests` (HTTP), `cloudinary` (video hosting), `python-dotenv` (secrets), `schedule` (timing)

---

### Task 1: Project Setup

**Files:**
- Create: `requirements.txt`
- Create: `.env`
- Create: `.gitignore`
- Create: `content/pending/.gitkeep`
- Create: `content/posted/.gitkeep`

- [ ] **Step 1: Create project structure**

```
insta automation/
├── content/
│   ├── pending/      ← drop video folders here
│   └── posted/       ← automation moves them here after posting
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── cloudinary_uploader.py
│   ├── instagram_api.py
│   ├── poster.py
│   └── scheduler.py
├── tests/
│   ├── __init__.py
│   ├── test_config.py
│   ├── test_cloudinary_uploader.py
│   ├── test_instagram_api.py
│   └── test_poster.py
├── main.py
├── requirements.txt
├── .env
└── .gitignore
```

- [ ] **Step 2: Create requirements.txt**

```
requests>=2.31.0
python-dotenv>=1.0.0
cloudinary>=1.36.0
schedule>=1.2.0
pytest>=7.4.0
```

- [ ] **Step 3: Create .gitignore**

```
.env
__pycache__/
*.pyc
.pytest_cache/
content/pending/*/
content/posted/*/
automation.log
```

- [ ] **Step 4: Create .env.example (committed) and .env (local only)**

`.env.example` (committed to git):
```
INSTAGRAM_ACCOUNT_ID=your_account_id
INSTAGRAM_ACCESS_TOKEN=your_long_lived_token_here
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
FB_APP_ID=your_app_id
FB_APP_SECRET=your_app_secret
POSTS_PER_DAY=10
```

`.env` (local only, never committed):
```
INSTAGRAM_ACCOUNT_ID=your_account_id
INSTAGRAM_ACCESS_TOKEN=your_long_lived_token_here
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
FB_APP_ID=your_app_id
FB_APP_SECRET=your_app_secret
POSTS_PER_DAY=10
```

- [ ] **Step 5: Create directory structure**

Run:
```bash
mkdir -p src tests content/pending content/posted
touch src/__init__.py tests/__init__.py content/pending/.gitkeep content/posted/.gitkeep
```

- [ ] **Step 6: Install dependencies**

Run: `pip install -r requirements.txt`
Expected: All packages install successfully

- [ ] **Step 7: Commit**

```bash
git init
git add requirements.txt .gitignore .env.example content/pending/.gitkeep content/posted/.gitkeep src/__init__.py tests/__init__.py
git commit -m "chore: initialize project structure"
```

---

### Task 2: Configuration Module

**Files:**
- Create: `src/config.py`
- Test: `tests/test_config.py`

- [ ] **Step 1: Write the failing test**

```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_config.py -v`
Expected: FAIL with "ModuleNotFoundError" or "ImportError"

- [ ] **Step 3: Write minimal implementation**

```python
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_config.py -v`
Expected: All 3 tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/config.py tests/test_config.py
git commit -m "feat: add configuration module with env var loading"
```

---

### Task 3: Cloudinary Uploader

**Files:**
- Create: `src/cloudinary_uploader.py`
- Test: `tests/test_cloudinary_uploader.py`

- [ ] **Step 1: Write the failing test**

```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_cloudinary_uploader.py -v`
Expected: FAIL with ImportError

- [ ] **Step 3: Write minimal implementation**

```python
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_cloudinary_uploader.py -v`
Expected: All 2 tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/cloudinary_uploader.py tests/test_cloudinary_uploader.py
git commit -m "feat: add Cloudinary video uploader"
```

---

### Task 4: Instagram Graph API Client

**Files:**
- Create: `src/instagram_api.py`
- Test: `tests/test_instagram_api.py`

- [ ] **Step 1: Write the failing test for creating a media container**

```python
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
        account_id="YOUR_ACCOUNT_ID",
        access_token="token123",
        video_url="https://example.com/video.mp4",
        caption="Test caption #hashtag",
    )

    assert result == "container_123"
    mock_post.assert_called_once()
    call_kwargs = mock_post.call_args
    assert "YOUR_ACCOUNT_ID" in call_kwargs[0][0]


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
        account_id="YOUR_ACCOUNT_ID",
        access_token="token123",
        container_id="container_123",
    )

    assert result == "media_456"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_instagram_api.py -v`
Expected: FAIL with ImportError

- [ ] **Step 3: Write minimal implementation**

```python
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_instagram_api.py -v`
Expected: All 3 tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/instagram_api.py tests/test_instagram_api.py
git commit -m "feat: add Instagram Graph API client for media publishing"
```

---

### Task 5: Poster Module (orchestrates upload → create → wait → publish)

**Files:**
- Create: `src/poster.py`
- Test: `tests/test_poster.py`

- [ ] **Step 1: Write the failing test**

```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_poster.py -v`
Expected: FAIL with ImportError

- [ ] **Step 3: Write minimal implementation**

```python
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_poster.py -v`
Expected: All 6 tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/poster.py tests/test_poster.py
git commit -m "feat: add poster module for orchestrating upload and publish"
```

---

### Task 6: Scheduler

**Files:**
- Create: `src/scheduler.py`
- Test: `tests/test_scheduler.py`

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_scheduler.py
import random
from datetime import datetime
from unittest.mock import patch
from src.scheduler import calculate_post_times, should_post_now


def test_calculate_post_times_returns_correct_count():
    random.seed(42)
    times = calculate_post_times(10)
    assert len(times) == 10


def test_calculate_post_times_within_bounds():
    random.seed(42)
    times = calculate_post_times(10)
    for t in times:
        hour = int(t.split(":")[0])
        assert 8 <= hour <= 22


def test_should_post_now_within_tolerance():
    now = datetime.now()
    time_str = f"{now.hour:02d}:{now.minute:02d}"
    assert should_post_now([time_str], tolerance_minutes=5) is True


def test_should_post_now_outside_tolerance():
    assert should_post_now(["03:00"], tolerance_minutes=5) is False
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_scheduler.py -v`
Expected: FAIL with ImportError

- [ ] **Step 3: Write the scheduler**

```python
# src/scheduler.py
import random
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


def calculate_post_times(posts_per_day: int) -> list[str]:
    """Generate evenly-spaced posting times with random jitter (8am-10pm).
    Seeded by today's date so restarts produce the same schedule."""
    random.seed(datetime.now().date().isoformat())
    start_hour = 8
    end_hour = 22
    total_minutes = (end_hour - start_hour) * 60
    interval = total_minutes // posts_per_day

    times = []
    for i in range(posts_per_day):
        base_minutes = start_hour * 60 + i * interval
        jitter = random.randint(-15, 15)
        actual_minutes = max(start_hour * 60, min(end_hour * 60, base_minutes + jitter))

        hour = actual_minutes // 60
        minute = actual_minutes % 60
        times.append(f"{hour:02d}:{minute:02d}")

    return times


def should_post_now(post_times: list[str], tolerance_minutes: int = 5) -> bool:
    """Check if current time matches any scheduled post time within tolerance."""
    now = datetime.now()
    for time_str in post_times:
        hour, minute = map(int, time_str.split(":"))
        scheduled = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        diff = abs((now - scheduled).total_seconds())
        if diff <= tolerance_minutes * 60:
            return True
    return False
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_scheduler.py -v`
Expected: All 4 tests PASS

- [ ] **Step 5: Run all tests**

Run: `python -m pytest tests/ -v`
Expected: All tests PASS

- [ ] **Step 6: Commit**

```bash
git add src/scheduler.py tests/test_scheduler.py
git commit -m "feat: add scheduler with jittered post times"
```

---

### Task 7: Main Entry Point

**Files:**
- Create: `main.py`

- [ ] **Step 1: Write main.py**

```python
# main.py
import time
import logging
import sys

from src.config import get_config
from src.poster import find_pending_posts, post_content, move_to_posted
from src.scheduler import calculate_post_times, should_post_now

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("automation.log"),
    ],
)
logger = logging.getLogger(__name__)

PENDING_DIR = "content/pending"
POSTED_DIR = "content/posted"


def run_once(config: dict) -> None:
    """Check for pending posts and publish the next one."""
    posts = find_pending_posts(PENDING_DIR)
    if not posts:
        logger.info("No pending posts found.")
        return

    post = posts[0]
    logger.info(f"Processing: {post['folder_name']}")

    try:
        media_id = post_content(post, config)
        move_to_posted(post["folder_path"], POSTED_DIR)
        logger.info(f"Successfully posted: {post['folder_name']} (ID: {media_id})")
    except Exception as e:
        logger.error(f"Failed to post {post['folder_name']}: {e}")


def run_scheduler(config: dict) -> None:
    """Run the scheduler loop — posts at scheduled times throughout the day."""
    post_times = calculate_post_times(config["posts_per_day"])
    logger.info(f"Scheduled post times for today: {post_times}")

    posted_times = set()

    while True:
        for time_str in post_times:
            if time_str not in posted_times and should_post_now([time_str]):
                run_once(config)
                posted_times.add(time_str)

        time.sleep(60)


def main():
    config = get_config()
    logger.info("Instagram Automation starting...")
    logger.info(f"Account ID: {config['instagram_account_id']}")
    logger.info(f"Posts per day: {config['posts_per_day']}")

    if "--once" in sys.argv:
        run_once(config)
    else:
        run_scheduler(config)


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Test the --once mode with a dry run**

Create a test post:
```bash
mkdir -p content/pending/test-post-001
echo "Testing my first automated post! 🚀 #automation #instagram" > content/pending/test-post-001/caption.txt
```

Then put any short `.mp4` video file in `content/pending/test-post-001/`.

- [ ] **Step 3: Run the automation**

Run: `python main.py --once`
Expected: Video uploads to Cloudinary, gets published to Instagram, folder moves to `content/posted/`

- [ ] **Step 4: Commit**

```bash
git add main.py
git commit -m "feat: add main entry point with scheduler and one-shot mode"
```

---

### Task 8: Token Refresh Utility

**Files:**
- Create: `src/token_refresh.py`

The long-lived token expires in 60 days. This utility refreshes it before expiry.

- [ ] **Step 1: Write the token refresh script**

```python
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
```

- [ ] **Step 2: Commit**

```bash
git add src/token_refresh.py
git commit -m "feat: add token refresh utility for 60-day token renewal"
```

---

## Content Folder Convention

Each post is a subfolder in `content/pending/` containing:

```
content/pending/
├── 001-motivational-reel/
│   ├── video.mp4        ← the video file (mp4, mov, avi, or mkv)
│   └── caption.txt      ← the caption text (with hashtags)
├── 002-product-showcase/
│   ├── reel.mov
│   └── caption.txt
```

After posting, the folder moves to `content/posted/`.

---

## Running the Automation

**One-shot mode** (post the next pending item):
```bash
python main.py --once
```

**Scheduler mode** (runs all day, posts at scheduled times):
```bash
python main.py
```

**Refresh token** (run before 60-day expiry):
```bash
python -m src.token_refresh
```

---

## Pre-requisites Before First Run

1. Sign up for Cloudinary at cloudinary.com (free, no credit card)
2. Copy your Cloud Name, API Key, and API Secret to `.env`
3. Fill in your Instagram access token in `.env`
4. Drop a video + caption.txt folder into `content/pending/`
5. Run `python main.py --once`
