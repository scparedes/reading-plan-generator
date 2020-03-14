from datetime import datetime, timedelta, date
import calendar
import csv
import argparse
from math import ceil
import os
import xlsxwriter
import string

PAGE_ROW_LIMIT = 35
PAGE_COLUMN_LIMIT = 13

WEEKDAYS = {'SUNDAY':6,
            'MONDAY':0,
            'TUESDAY':1,
            'WEDNESDAY':2,
            'THURSDAY':3,
            'FRIDAY':4,
            'SATURDAY':5}
START_OF_WEEK = WEEKDAYS['MONDAY']

class ReadingPlan(object):
    def __init__(self, from_date=None, to_date=None, startpage=None, endpage=None, frequency=None):
        self.from_date = from_date
        self.to_date = to_date
        self.startpage = startpage
        self.endpage = endpage
        self.frequency = frequency

    @property
    def pages(self):
        return [i for i in range(self.startpage, self.endpage+1)]

    def get_page_placeholders(self):
        return [None for i in range(0, self.endpage-self.startpage+1)]

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
            day.startpage = day.endpage = pages.pop(0)
            for d in empty_day[1:]:
                day.endpage = pages.pop(0)

    def structure_days(self):
        self.days = []
        cur_date = self.from_date
        while not (cur_date > self.to_date):
            self.days.append(ReadingPlan(from_date=cur_date, to_date=cur_date))
            cur_date += timedelta(days=1)

class BookReadingPlan(ReadingPlan):
    def __init__(self, from_date=None, to_date=None, startpage=None, endpage=None, frequency=5, outdir=None):
        super(BookReadingPlan, self).__init__(from_date, to_date, startpage, endpage, frequency)
        self.outdir = outdir
        self.outfile = os.path.join(outdir, 'reading-plan')
        self.weeks = []

    def generate_plan_as_csv(self):
        outfile = self.outfile+'.csv'
        months = calendar.month_name
        self.populate_weeks()
        readingplan = open(os.path.expanduser(outfile), 'w')
        csv_writer = csv.writer(readingplan, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for week in self.weeks:
            if not week.days:
                continue
            month_name = months[week.from_date.month]
            csv_writer.writerow(['%s, week %d' % (month_name, week_of_month(week.from_date))])
            for day in week.days:
                if not day.startpage:
                    continue
                if day.startpage == day.endpage:
                    csv_writer.writerow(['o ' + '%d' % (day.startpage)])
                else:
                    csv_writer.writerow(['o ' + '%d-%d' % (day.startpage, day.endpage)])

    def generate_plan_as_excel(self):
        COLUMNS = dict(enumerate(string.ascii_uppercase, 1))
        def cell(column, row):
            return '%s%s' % (COLUMNS[column], row)
        outfile = os.path.expanduser(self.outfile)+'.xlsx'
        if os.path.exists(outfile):
            os.remove(outfile)
        row_limit = PAGE_ROW_LIMIT
        column_limit = PAGE_COLUMN_LIMIT
        column_increment = 2
        column_overflow_buffer = column_limit - 1
        workbook = xlsxwriter.Workbook(outfile)
        worksheet = workbook.add_worksheet()
        worksheet.set_landscape()
        bold = workbook.add_format({'bold': True})
        months = calendar.month_name
        self.populate_weeks()
        row = 1
        column = 1
        page = 0
        for week in self.weeks:
            if not week.days:
                continue
            month_name = months[week.from_date.month]
            if len(week.days) + 1 + (row - page * row_limit) > row_limit:
                column += column_increment
                row = 1 + page * row_limit
                if column > column_overflow_buffer:
                    column = 1
                    page += 1
                    row = 1 + page * row_limit
            worksheet.write(cell(column, row), '%s, week %d' % (month_name, week_of_month(week.from_date)), bold)
            row += 1
            for day in week.days:
                if not day.startpage:
                    continue
                if day.startpage == day.endpage:
                    worksheet.write(cell(column, row), 'o  ' + '%d' % (day.startpage))
                else:
                    worksheet.write(cell(column, row), 'o  ' + '%d-%d' % (day.startpage, day.endpage))
                row += 1
        worksheet.set_v_pagebreaks([1 + i * row_limit for i in range(1, page)])
        workbook.close()

    def populate_weeks(self):
        self.structure_weeks()
        placeholders = self.get_page_placeholders()
        splits = min(len(self.weeks), int(ceil(len(self.pages)/self.frequency)))
        empty_weeks = split_n_times(placeholders, splits)
        # evenly distributed weeks
        pages = self.pages
        for week, empty_week in zip(self.weeks, empty_weeks):
            print(week.from_date, week.to_date)
            week.startpage = week.endpage = pages.pop(0)
            for day in empty_week[1:]:
                week.endpage = pages.pop(0)
            week.populate_days()

    def structure_weeks(self):
        self.weeks = []
        cur_date = self.from_date
        first_week_day = self.from_date
        while not (cur_date > self.to_date):
            if cur_date.weekday() == 6:
                last_week_day = cur_date - timedelta(days=1)
                print (cur_date, first_week_day, last_week_day)
                self.weeks.append(WeeklyReadingPlan(from_date=first_week_day, to_date=last_week_day, frequency=self.frequency))
                first_week_day = cur_date
            cur_date += timedelta(days=1)
        if last_week_day != cur_date:
            last_week_day = cur_date - timedelta(days=1)
            print (cur_date, first_week_day, last_week_day)
            self.weeks.append(WeeklyReadingPlan(from_date=first_week_day, to_date=last_week_day, frequency=self.frequency))

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
        return [items[i:i+batch_size] for i in range(0, len(items), batch_size)]

def split_n_times(items, n):
    n = min(len(items), n)
    return [items[i*len(items)//n:(i+1)*len(items)//n] for i in range(0, n)]

def week_of_month(dt):
    first_day = dt.replace(day=1)
    adjusted_dom = dt.day + first_day.weekday() + ((7 - START_OF_WEEK) % 7)
    week_num = int(ceil(adjusted_dom/7.0))
    return week_num - ((7 - START_OF_WEEK) % 7)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--from-date', required=True)
    parser.add_argument('--to-date', required=True)
    parser.add_argument('--start-page', required=True, type=int)
    parser.add_argument('--end-page', required=True, type=int)
    parser.add_argument('--frequency', type=int, default=5)
    parser.add_argument('--outdir', default='~/Desktop/')
    (options, args) = parser.parse_known_args()

    from_date = datetime.strptime(options.from_date, '%Y%m%d')
    to_date = datetime.strptime(options.to_date, '%Y%m%d')
    cur_date = from_date

    weekly_reading_plan = BookReadingPlan(from_date=from_date, 
                                          to_date=to_date, 
                                          startpage=options.start_page, 
                                          endpage=options.end_page,
                                          frequency=options.frequency,
                                          outdir=options.outdir)
    weekly_reading_plan.generate_plan_as_excel()