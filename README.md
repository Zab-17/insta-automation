# Instagram Automation

Auto-posts reels to Instagram from a local folder. Drop a video + caption, it handles the rest.

## Setup

1. `pip install -r requirements.txt`
2. Copy `.env.example` to `.env` and fill in your credentials
3. Create folders: `mkdir -p content/pending content/posted`

## Usage

**Add a post:** Create a subfolder in `content/pending/` with a video file (`.mp4`/`.mov`) and a `caption.txt`.

```
content/pending/
  my-reel/
    video.mp4
    caption.txt
```

**Run the watcher** (polls every 30s, posts everything it finds):

```bash
python main.py
```

**One-shot mode** (post all pending and exit):

```bash
python main.py --once
```

**Refresh token** (before 60-day expiry):

```bash
python -m src.token_refresh
```

## How It Works

1. Watches `content/pending/` for new subfolders
2. Uploads video to Cloudinary (gets a public URL)
3. Creates an Instagram media container via Graph API
4. Waits for processing, then publishes
5. Moves the folder to `content/posted/`
