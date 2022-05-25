from datetime import datetime
import time


def datetime_to_unix(date: datetime):
    return int(time.mktime(date.timetuple()))
