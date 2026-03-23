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
