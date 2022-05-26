from datetime import datetime, timedelta
import time


def datetime_to_unix(date: datetime):
    return int(time.mktime(date.timetuple()))


def now():
    return datetime.now()


def add_days(date: datetime, days):
    return date + timedelta(days=int(days))
