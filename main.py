# main.py
import time
import logging
import sys

from src.config import get_config
from src.poster import find_pending_posts, post_content, move_to_posted

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
POLL_INTERVAL = 30  # seconds between folder checks


def post_all_pending(config: dict) -> int:
    """Post every pending item. Returns count of successful posts."""
    posts = find_pending_posts(PENDING_DIR)
    if not posts:
        return 0

    posted = 0
    for post in posts:
        logger.info(f"Processing: {post['folder_name']}")
        try:
            media_id = post_content(post, config)
            move_to_posted(post["folder_path"], POSTED_DIR)
            logger.info(f"Posted: {post['folder_name']} (ID: {media_id})")
            posted += 1
        except Exception as e:
            logger.error(f"Failed: {post['folder_name']}: {e}")

    return posted


def watch(config: dict) -> None:
    """Poll the pending folder and post anything that appears."""
    logger.info(f"Watching {PENDING_DIR}/ every {POLL_INTERVAL}s — drop folders to auto-post")
    while True:
        count = post_all_pending(config)
        if count:
            logger.info(f"Batch done — {count} posted")
        time.sleep(POLL_INTERVAL)


def main():
    config = get_config()
    logger.info("Instagram Automation starting...")
    logger.info("Account ID: ****" + config['instagram_account_id'][-4:])

    if "--once" in sys.argv:
        n = post_all_pending(config)
        logger.info(f"Done — {n} posted" if n else "No pending posts found.")
    else:
        watch(config)


if __name__ == "__main__":
    main()
