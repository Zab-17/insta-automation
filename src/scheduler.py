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
