"""
Calculate train speed
"""

import datetime
from collections import defaultdict, deque


class SpeedStat:
    """
    Calculate train speed
    """

    def __init__(self):
        self.queue = deque(maxlen=100)
        self.stat = defaultdict(int)

    def add_color(self, color):
        """
        Add color to stat
        """

        self.queue.append((datetime.datetime.now(), color))
        self.stat[color] += 1

    def get_stat(self):
        """
        Get speed stat
        """

        cnt = 0
        for color in self.stat:
            cnt += self.stat[color]

        if not cnt:
            return None

        colors = []
        for color, color_cnt in self.stat.items():
            colors.append(f'{color}: {int(color_cnt * 100 / cnt)}')
        return ', '.join(colors)

    def get_speed(self) -> int:
        """
        Get current speed
        """

        interval_seconds = 3
        time_interval = datetime.timedelta(seconds=interval_seconds)
        now_ = datetime.datetime.now()
        cnt = 0
        for date_time, _ in reversed(self.queue):
            interval_ = now_ - date_time
            if interval_ > time_interval:
                break
            cnt += 1

        brick_size = 0.008
        brick_width = 2  # 2 stud
        sec_in_hour = 3600
        meters_in_hour = int(cnt * brick_size * brick_width * sec_in_hour / interval_seconds)
        return meters_in_hour
