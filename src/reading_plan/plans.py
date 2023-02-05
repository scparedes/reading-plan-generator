from datetime import datetime, timedelta
from typing import Any, List


from common import START_OF_WEEK


YEAR_LIMIT = 3


class ReadingPlan:
    """A minimalist reading plan.
    """

    def __init__(self,
                 start_date: datetime = None,
                 end_date: datetime = None,
                 startpage: int = None,
                 endpage: int = None,
                 frequency: int = 5,
                 name: str = None):
        self.start_date = start_date
        self.end_date = end_date
        self.startpage = startpage
        self.endpage = endpage
        self.frequency = frequency
        self.name = name

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

    def __init__(self,
                 start_date: datetime = None,
                 end_date: datetime = None,
                 startpage: int = None,
                 endpage: int = None,
                 frequency: int = 5,
                 name: str = None):
        super(WeekLongReadingPlan, self).__init__(
            start_date, end_date, startpage, endpage, frequency, name)
        self.days = []


class BookReadingPlan(ReadingPlan):
    """A reading plan based off multiple weeks of reading.
    """

    def __init__(self,
                 start_date: datetime = None,
                 end_date: datetime = None,
                 startpage: int = None,
                 endpage: int = None,
                 frequency: int = 5,
                 name: str = None):
        super(BookReadingPlan, self).__init__(
            start_date, end_date, startpage, endpage, frequency, name)
        if start_date > end_date:
            raise ValueError('Start Date must be smaller than End Date!')
        if (end_date - start_date).days > 365 * YEAR_LIMIT:
            raise ValueError(
                'Plans can only be generated for 3 years of reading or less!')
        self.weeks = []
        self.populate_weeks()

    def populate_weeks(self):
        pages = self.pages
        dates = self.get_dates_in_plan()
        split_pages = split_n_times(pages, len(dates))
        days = []
        for d, pages in zip(dates, split_pages):
            if d.weekday() == START_OF_WEEK and d != self.start_date:
                if self.frequency != 1 or days:
                    week_long_plan = self.create_week_long_plan(days)
                    self.weeks.append(week_long_plan)
                    days = []
            startpage = endpage = pages.pop(0)
            for page in pages[1:]:
                endpage = page
            day = ReadingPlan(start_date=d,
                              end_date=d,
                              startpage=startpage,
                              endpage=endpage)
            days.append(day)
        if days:
            week_long_plan = self.create_week_long_plan(days)
            self.weeks.append(week_long_plan)

    def create_week_long_plan(self, days: List[datetime]):
        if days[-1].end_date == self.end_date:
            end_date = self.end_date
        else:
            cur_date = days[-1].end_date
            while (cur_date.weekday() != START_OF_WEEK or
                   cur_date == days[0].start_date):
                cur_date += timedelta(days=1)
            end_date = cur_date - timedelta(days=1)
        week_long_plan = WeekLongReadingPlan(start_date=days[0].start_date,
                                             end_date=end_date,
                                             startpage=days[0].startpage,
                                             endpage=days[-1].endpage,
                                             frequency=self.frequency)
        week_long_plan.days = days
        return week_long_plan

    def get_dates_in_plan(self):
        all_dates = get_days(self.start_date, self.end_date)
        dates = self.adjust_dates_for_reading_frequency(all_dates)
        return dates

    def adjust_dates_for_reading_frequency(self, all_dates: List[datetime]):
        dates = []
        cur_date = all_dates[0]
        dates_per_week = 0
        if self.frequency == 1:
            dates.append(cur_date)
        while not (cur_date > self.end_date):
            dates_per_week += 1
            if (cur_date.weekday() == START_OF_WEEK and
                cur_date != self.start_date):
                dates_per_week = 0
            if dates_per_week >= self.frequency:
                cur_date += timedelta(days=1)
                continue
            dates.append(cur_date)
            cur_date += timedelta(days=1)
        return dates


def get_days(from_date: datetime, to_date: datetime):
    days = []
    if from_date and to_date:
        cur_day = from_date
        while cur_day <= to_date:
            days.append(cur_day)
            cur_day += timedelta(days=1)
    return days


def split_n_times(items: List[Any], n: int):
    n = min(len(items), n)
    return [items[i*len(items)//n:(i+1)*len(items)//n] for i in range(0, n)]
