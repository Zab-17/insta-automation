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
    logger.info("Account ID: ****" + config['instagram_account_id'][-4:])
    logger.info(f"Posts per day: {config['posts_per_day']}")

    if "--once" in sys.argv:
        run_once(config)
    else:
        run_scheduler(config)


if __name__ == "__main__":
    main()
