from datetime import datetime, timedelta, date
import calendar
from random import choice
import csv
import argparse

READING_PLAN_PATH = '/Users/santi/Desktop/readingplan.csv'

class ReadingPlan(object):
    def __init__(self, from_date=None, to_date=None, startpage=None, endpage=None, frequency=None):
        self.from_date = from_date
        self.to_date = to_date
        self.startpage = startpage
        self.endpage = endpage
        self.frequency = frequency

class WeeklyReadingPlan(ReadingPlan):
    def __init__(self, from_date=None, to_date=None, startpage=None, endpage=None, frequency=5):
        super(WeeklyReadingPlan, self).__init__(from_date, to_date, startpage, endpage, frequency)
        self.days = []

    def populate_days(self):
        self.structure_days()
        placeholders = self.get_page_placeholders()
        empty_days = split_n_times(placeholders, min(self.frequency, len(self.days)))
        pages = self.pages
        for day, empty_day in zip(self.days, empty_days):
            day.startpage = pages.pop(0)
            for d in empty_day[1:]:
                day.endpage = pages.pop(0)

    def structure_days(self):
        self.days = []
        cur_date = self.from_date
        while not (cur_date > self.to_date):
            self.days.append(ReadingPlan(from_date=cur_date, to_date=cur_date))
            cur_date += timedelta(days=1)

    @property
    def pages(self):
        return [i for i in xrange(self.startpage, self.endpage+1)]

    def get_page_placeholders(self):
        return [None for i in xrange(0, self.endpage-self.startpage+1)]

class BookReadingPlan(ReadingPlan):
    def __init__(self, from_date=None, to_date=None, startpage=None, endpage=None, frequency=5):
        super(BookReadingPlan, self).__init__(from_date, to_date, startpage, endpage, frequency)
        self.weeks = []

    def generate_plan(self):
        months = calendar.month_name
        self.populate_weeks()
        readingplan = open(READING_PLAN_PATH, 'w')
        csv_writer = csv.writer(readingplan, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for week_num, week in enumerate(self.weeks):
            month_name = months[week.from_date.month]
            csv_writer.writerow(['%s, week %d' % (month_name, week_num+1)])
            for day in week.days:
                if not day.startpage:
                    continue
                csv_writer.writerow(['o  '+'%d-%d' % (day.startpage, day.endpage)])

    def populate_weeks(self):
        self.structure_weeks()
        placeholders = self.get_page_placeholders()
        empty_weeks = split_n_times(placeholders, len(self.weeks))
        # evenly distributed weeks
        pages = self.pages
        for week, empty_week in zip(self.weeks, empty_weeks):
            week.startpage = pages.pop(0)
            for day in empty_week[1:]:
                week.endpage = pages.pop(0)
            week.populate_days()

    def structure_weeks(self):
        self.weeks = []
        cur_date = self.from_date
        first_week_day = self.from_date
        week_last_seen = cur_date.date().isocalendar()[1]
        while not (cur_date > self.to_date):
            calendar_week = cur_date.date().isocalendar()[1]
            if week_last_seen != calendar_week:
                last_week_day = cur_date - timedelta(days=1)
                self.weeks.append(WeeklyReadingPlan(from_date=first_week_day, to_date=last_week_day, frequency=self.frequency))
                week_last_seen = cur_date.date().isocalendar()[1]
                first_week_day = cur_date
            cur_date += timedelta(days=1)

    @property
    def pages(self):
        return [i for i in xrange(self.startpage, self.endpage+1)]

    def get_page_placeholders(self):
        return [None for i in xrange(0, self.endpage-self.startpage+1)]

def split_into_batches(items, batch_size, return_iterator=False):
    def iterator():
        batch = []
        for item in items:
             batch.append(item)
             if len(batch) >= batch_size:
                 yield batch
                 batch = []
        if len(batch) > 0:
            yield batch
    if return_iterator:
        return iterator()
    else:
        return [items[i:i+batch_size] for i in xrange(0, len(items), batch_size)]

def split_n_times(items, n):
    n = min(len(items), n)
    return [items[i*len(items)/n:(i+1)*len(items)/n] for i in xrange(0, n)]

def get_days(from_date, to_date):
    days = []
    if from_date and to_date:
        cur_day = from_date
        while cur_day <= date:
            days.append(cur_day)
            cur_day += timedelta(days=1)
    return days

if __name__ == '__main__':
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--from-date', required=True)
    parser.add_argument('--to-date', required=True)
    parser.add_argument('--start-page', required=True, type=int)
    parser.add_argument('--end-page', required=True, type=int)
    parser.add_argument('--frequency', type=int, default=5)
    (options, args) = parser.parse_known_args()

    from_date = datetime.strptime(options.from_date, '%Y%m%d')
    to_date = datetime.strptime(options.to_date, '%Y%m%d')
    cur_date = from_date

    weekly_reading_plan = BookReadingPlan(from_date=from_date, 
                                          to_date=to_date, 
                                          startpage=options.start_page, 
                                          endpage=options.end_page,
                                          frequency=options.frequency)
    weekly_reading_plan.generate_plan()


    print 'done'