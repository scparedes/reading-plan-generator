"""Functions and variables that are used across many app and library files."""
from datetime import datetime
from math import ceil


# The day-key used will mark the 1st day of the week in the reading plans.
START_OF_WEEK = {'SUNDAY': 6,
                 'MONDAY': 0,
                 'TUESDAY': 1,
                 'WEDNESDAY': 2,
                 'THURSDAY': 3,
                 'FRIDAY': 4,
                 'SATURDAY': 5}['MONDAY']


# TODO: Verify that this method is working and use in writers.py.
def week_of_month(d: datetime):
    first_day = d.replace(day=1)
    adjusted_dom = d.day + first_day.weekday() + ((7 - START_OF_WEEK) % 7)
    week_num = int(ceil(adjusted_dom/7.0))
    return week_num - ((7 - START_OF_WEEK) % 7)
