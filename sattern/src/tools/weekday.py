from datetime import datetime, timedelta, date, time
from typing import List

"""Returns a list of datetime objects during specified business hours (UTC)"""

class weekday():

    def __init__(self, days: List = [0, 1, 2, 3, 4], day_start: str = "14:30", day_end: str = "20:30", increment_hours: int = 1, increment_minutes: int = 0):
        self.day_start = datetime.strptime(day_start, "%H:%M").time()
        self.day_end = datetime.strptime(day_end, "%H:%M").time()
        self.increment_hours = increment_hours
        self.increment_minutes = increment_minutes

        self.business_hours = {
            0: True if 0 in days else False,  # Monday
            1: True if 1 in days else False,  # Tuesday
            2: True if 2 in days else False,  # Wednesday
            3: True if 3 in days else False,  # Thursday
            4: True if 4 in days else False,  # Friday
            5: True if 5 in days else False,  # Saturday
            6: True if 6 in days else False,  # Sunday
        }

        self.holidays = [
            date(2023, 5, 1)
        ]

    def is_in_open_day(self, dt: datetime) -> bool:
        return self.business_hours.get(dt.weekday()) and dt.date() not in self.holidays

    def is_in_open_hours(self, dt: datetime) -> bool:
        return self.is_in_open_day(dt) and self.day_start <= dt.time() < self.day_end

    def get_next_open_datetime(self, dt: datetime) -> datetime:
        dt = dt + timedelta(hours=self.increment_hours, minutes=self.increment_minutes)
        if dt.time() < self.day_start:
            dt = datetime.combine(dt.date(), self.day_start)
        elif dt.time() > self.day_end:
            dt = datetime.combine(dt.date(), self.day_start)
            while not self.is_in_open_day(dt):
                dt = dt + timedelta(days=1)

        return dt

    def get_next_n_datetimes(self, n: int, start: datetime):
        next_dates: List[datetime] = []
        for _ in range(n):
            if len(next_dates) == 0:
                next_dates.append(self.get_next_open_datetime(start))
            else:
                next_dates.append(self.get_next_open_datetime(next_dates[-1]))

        return next_dates

