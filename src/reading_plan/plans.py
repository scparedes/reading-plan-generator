"""Defines various reading plans.
"""
from datetime import datetime, timedelta
from typing import Any, List


from common import START_OF_WEEK


YEAR_LIMIT = 3


class ReadingPlan:
    """A minimalist reading plan.

    Args:
        start_date: The beginning of the reading plan.
        end_date: The end of the reading plan.
        start_page: The first page of the reading plan.
        end_page: The last page of the reading plan.
        num_times_to_read: The number of times to read during the reading plan.
        name: The name of the reading plan.
    """

    def __init__(self,
                 start_date: datetime = None,
                 end_date: datetime = None,
                 start_page: int = None,
                 end_page: int = None,
                 num_times_to_read: int = 5,
                 name: str = None):
        self.start_date = start_date
        self.end_date = end_date
        self.start_page = start_page
        self.end_page = end_page
        self.num_times_to_read = num_times_to_read
        self.name = name
        self.days = []

    @property
    def pages(self) -> List[int]:
        """The list of page numbers to read."""
        return range(self.start_page, self.end_page+1)

    @property
    def formatted_date_range(self) -> str:
        """The start date and end date as a human-readable string."""
        fdr = '%s %d' % (self.start_date.strftime('%b'), self.start_date.day)
        if self.start_date != self.end_date:
            fdr += ' - '
            if self.start_date.month != self.end_date.month:
                fdr += '%s ' % self.end_date.strftime('%b')
            fdr += str(self.end_date.day)
        return fdr


class BookReadingPlan(ReadingPlan):
    """A reading plan based off multiple weeks of reading.

    Args:
        start_date: The beginning of the reading plan.
        end_date: The end of the reading plan.
        start_page: The first page of the reading plan.
        end_page: The last page of the reading plan.
        num_times_to_read: The number of times to read during the reading plan.
        name: The name of the reading plan.
    """

    def __init__(self,
                 start_date: datetime = None,
                 end_date: datetime = None,
                 start_page: int = None,
                 end_page: int = None,
                 num_times_to_read: int = 5,
                 name: str = None):
        super(BookReadingPlan, self).__init__(
            start_date, end_date, start_page, end_page, num_times_to_read, name)
        if start_date > end_date:
            raise ValueError('Start Date must be smaller than End Date!')
        if (end_date - start_date).days > 365 * YEAR_LIMIT:
            raise ValueError(
                'Plans can only be generated for 3 years of reading or less!')
        self.weeks = []
        self.populate_weeks()

    def populate_weeks(self):
        """Generates a multi-week reading plan and stores it in self.weeks."""
        pages = self.pages
        dates = self.get_dates_in_plan()
        split_pages = _split_n_times(pages, len(dates))
        days = []
        for d, pages in zip(dates, split_pages):
            if d.weekday() == START_OF_WEEK and d != self.start_date:
                if self.num_times_to_read != 1 or days:
                    week_long_plan = self.create_week_long_plan(days)
                    self.weeks.append(week_long_plan)
                    days = []
            start_page = end_page = pages.pop(0)
            for page in pages[1:]:
                end_page = page
            day = ReadingPlan(start_date=d,
                              end_date=d,
                              start_page=start_page,
                              end_page=end_page)
            days.append(day)
        if days:
            week_long_plan = self.create_week_long_plan(days)
            self.weeks.append(week_long_plan)

    def create_week_long_plan(self, days: List[datetime]) -> ReadingPlan:
        """Generates a single-week reading plan.

        Args:
            days: The days of a reading plan.

        Returns:
            A single-week reading plan.
        """
        if days[-1].end_date == self.end_date:
            end_date = self.end_date
        else:
            cur_date = days[-1].end_date
            while (cur_date.weekday() != START_OF_WEEK or
                   cur_date == days[0].start_date):
                cur_date += timedelta(days=1)
            end_date = cur_date - timedelta(days=1)
        week_long_plan = ReadingPlan(start_date=days[0].start_date,
                                     end_date=end_date,
                                     start_page=days[0].start_page,
                                     end_page=days[-1].end_page,
                                     num_times_to_read=self.num_times_to_read)
        week_long_plan.days = days
        return week_long_plan

    def get_dates_in_plan(self) -> List[datetime]:
        """Gets the days in a reading plan.

        Returns:
            The days in a reading plan.
        """
        all_dates = _get_days(self.start_date, self.end_date)
        dates = self.adjust_dates_for_reading_frequency(all_dates)
        return dates

    def adjust_dates_for_reading_frequency(self, all_dates: List[datetime]):
        """Remaps consecutive days to days that satisfy the reading frequency.

        Returns:
            The days that satisfy the reading frequency per week.
        """
        dates = []
        cur_date = all_dates[0]
        dates_per_week = 0
        if self.num_times_to_read == 1:
            dates.append(cur_date)
        while not cur_date > self.end_date:
            dates_per_week += 1
            if (cur_date.weekday() == START_OF_WEEK and
                    cur_date != self.start_date):
                dates_per_week = 0
            if dates_per_week >= self.num_times_to_read:
                cur_date += timedelta(days=1)
                continue
            dates.append(cur_date)
            cur_date += timedelta(days=1)
        return dates


def _get_days(from_date: datetime, to_date: datetime) -> List[datetime]:
    days = []
    if from_date and to_date:
        cur_day = from_date
        while cur_day <= to_date:
            days.append(cur_day)
            cur_day += timedelta(days=1)
    return days


def _split_n_times(items: List[Any], n: int) -> List[List[Any]]:
    n = min(len(items), n)
    return [items[i*len(items)//n:(i+1)*len(items)//n] for i in range(0, n)]
