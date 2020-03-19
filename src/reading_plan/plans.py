# native python libs
from datetime import timedelta
from math import ceil
from common import WEEKDAYS, START_OF_WEEK


class ReadingPlan(object):
    """A minimalist reading plan.
    """
    def __init__(self, start_date=None, end_date=None, startpage=None, endpage=None, frequency=None):
        self.start_date = start_date
        self.end_date = end_date
        self.startpage = startpage
        self.endpage = endpage
        self.frequency = frequency

    @property
    def pages(self):
        return [i for i in range(self.startpage, self.endpage+1)]

    def get_page_placeholders(self):
        return [None for i in range(0, self.endpage-self.startpage+1)]

    @property
    def formatted_date_range(self):
        fdr = '%s %d' % (self.start_date.strftime('%b'), self.start_date.day)
        if self.start_date != self.end_date:
            fdr += ' - '
            if self.start_date.month != self.end_date.month:
                fdr += '%s ' % self.end_date.strftime('%b')
            fdr += str(self.end_date.day)
        return fdr

class WeekLongReadingPlan(ReadingPlan):
    """A reading plan based off of 1 week of reading.
    """
    def __init__(self, start_date=None, end_date=None, startpage=None, endpage=None, frequency=5):
        super(WeekLongReadingPlan, self).__init__(start_date, end_date, startpage, endpage, frequency)
        self.days = []

    def populate_days(self):
        self.structure_days()
        placeholders = self.get_page_placeholders()
        empty_days = split_n_times(placeholders, min(self.frequency, len(self.days)))
        pages = self.pages
        for day, empty_day in zip(self.days, empty_days):
            day.startpage = day.endpage = pages.pop(0)
            for _ in empty_day[1:]:
                day.endpage = pages.pop(0)

    def structure_days(self):
        self.days = []
        cur_date = self.start_date
        while not (cur_date > self.end_date):
            self.days.append(ReadingPlan(start_date=cur_date, end_date=cur_date))
            cur_date += timedelta(days=1)

class BookReadingPlan(ReadingPlan):
    """A reading plan based off multiple weeks of reading.
    """
    def __init__(self, start_date=None, end_date=None, startpage=None, endpage=None, frequency=5):
        super(BookReadingPlan, self).__init__(start_date, end_date, startpage, endpage, frequency)
        if start_date > end_date:
            raise ValueError('Start Date must be smaller than End Date!')
        if (end_date - start_date).days > 365 * 2:
            raise ValueError('Plans can only be generated for 2 years of reading or less!')
        self.weeks = []
        self.populate_weeks()

    def populate_weeks(self):
        self.structure_weeks()
        placeholders = self.get_page_placeholders()
        splits = min(len(self.weeks), int(ceil(len(self.pages)/self.frequency)))
        empty_weeks = split_n_times(placeholders, splits)
        # TODO: Normally distribute (or "evenly" pages) across weeks.
        pages = self.pages
        for week, empty_week in zip(self.weeks, empty_weeks):
            week.startpage = week.endpage = pages.pop(0)
            for _ in empty_week[1:]:
                week.endpage = pages.pop(0)
            week.populate_days()

    def structure_weeks(self):
        self.weeks = []
        cur_date = self.start_date
        first_week_day = self.start_date
        while not (cur_date > self.end_date):
            if cur_date.weekday() == START_OF_WEEK:
                last_week_day = cur_date - timedelta(days=1)
                self.weeks.append(WeekLongReadingPlan(start_date=first_week_day, end_date=last_week_day, frequency=self.frequency))
                first_week_day = cur_date
            cur_date += timedelta(days=1)
        if last_week_day != cur_date:
            last_week_day = cur_date - timedelta(days=1)
            self.weeks.append(WeekLongReadingPlan(start_date=first_week_day, end_date=last_week_day, frequency=self.frequency))

def split_n_times(items, n):
    n = min(len(items), n)
    return [items[i*len(items)//n:(i+1)*len(items)//n] for i in range(0, n)]