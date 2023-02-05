from datetime import datetime
from math import ceil


WEEKDAYS = {'SUNDAY': 6,
            'MONDAY': 0,
            'TUESDAY': 1,
            'WEDNESDAY': 2,
            'THURSDAY': 3,
            'FRIDAY': 4,
            'SATURDAY': 5}
START_OF_WEEK = WEEKDAYS['MONDAY']


def week_of_month(d: datetime):
    first_day = d.replace(day=1)
    adjusted_dom = d.day + first_day.weekday() + ((7 - START_OF_WEEK) % 7)
    week_num = int(ceil(adjusted_dom/7.0))
    return week_num - ((7 - START_OF_WEEK) % 7)
