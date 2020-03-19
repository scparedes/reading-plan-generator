# Native Python libraries
from datetime import datetime, timedelta, date
import calendar
import csv
import argparse
from math import ceil
import os
import string

# 3rd party libraries
import xlsxwriter

# Globals
WEEKDAYS = {'SUNDAY':6,
            'MONDAY':0,
            'TUESDAY':1,
            'WEDNESDAY':2,
            'THURSDAY':3,
            'FRIDAY':4,
            'SATURDAY':5}
num2words1 = {0:'Zero', 1: 'One', 2: 'Two', 3: 'Three', 4: 'Four', 5: 'Five', \
            6: 'Six', 7: 'Seven', 8: 'Eight', 9: 'Nine', 10: 'Ten', \
            11: 'Eleven', 12: 'Twelve', 13: 'Thirteen', 14: 'Fourteen', \
            15: 'Fifteen', 16: 'Sixteen', 17: 'Seventeen', 18: 'Eighteen', 19: 'Nineteen'}
num2words2 = ['Twenty', 'Thirty', 'Forty', 'Fifty', 'Sixty', 'Seventy', 'Eighty', 'Ninety']
START_OF_WEEK = WEEKDAYS['MONDAY']
MONTHS = calendar.month_name
DEFAULT_CELL = 0

PAGE_ROW_LIMIT = 35
PAGE_COLUMN_LIMIT = 15
COLUMN_INCREMENT = 2
COLUMNS = dict(enumerate(string.ascii_uppercase, 1))
def cell(column, row):
    return '%s%s' % (COLUMNS[column], row)

OUT_FILENAME = 'reading-plan'

class WeekLongWriter(object):
    """Writes a WeekLongReadingPlan to disk.
    """
    def __init__(self, 
                 outfile=None, 
                 format_outfile=True, 
                 row_limit=PAGE_ROW_LIMIT, 
                 column_limit=PAGE_COLUMN_LIMIT, 
                 column_increment=COLUMN_INCREMENT):
        self.outfile = outfile
        self.format_outfile = format_outfile
        self.open()
        self.page = 0
        self.row = 1
        self.column = 1
        self.row_limit = row_limit
        self.column_limit = column_limit
        self.column_increment = column_increment
        self.column_overflow_buffer = self.column_limit - 1

    def write_week(self, week):
        if not week.days:
            return
        month_name = MONTHS[week.from_date.month]
        if self.format_outfile:
            self.select_column_and_page(len(week.days))
        self.write_header('%s, week %d' % (month_name, week_of_month(week.from_date)))
        self.increment_row()
        for day in week.days:
            if not day.startpage:
                continue
            if day.startpage == day.endpage:
                self.write_data('o  ' + '%d' % (day.startpage))
            else:
                self.write_data('o  ' + '%d-%d' % (day.startpage, day.endpage))
            self.increment_row()

    def select_column_and_page(self, num_additional_rows):
        if self.additional_rows_will_fit_on_current_page(num_additional_rows):
            self.column += self.column_increment
            self.row = 1 + self.page * self.row_limit
            if self.column > self.column_overflow_buffer:
                self.column = 1
                self.page += 1
                self.row = 1 + self.page * self.row_limit

    def additional_rows_will_fit_on_current_page(self, num_rows):
        return num_rows + 1 + (self.row - self.page * self.row_limit) > self.row_limit

    def increment_row(self):
        self.row += 1

    def write_weekly_summary(self, weeks):
        self.increment_row()
        self.column_increment += 1
        self.select_column_and_page(1)
        self.write_header('Week to Read')
        self.increment_row()
        start_weeks = 1 if not weeks[0].from_date.weekday() else 0
        for overall_week_number, week in enumerate(weeks, start_weeks):
            if not week.days:
                continue
            self.select_column_and_page(1)
            weekly_summary_row = ('___ %s' % num_to_word(overall_week_number)).ljust(17, '.') + week.formatted_date_range
            self.write_data(weekly_summary_row)
            self.increment_row()

    def write_header(self, header_str):
        raise NotImplementedError

    def write_data(self, data_str):
        raise NotImplementedError

    def open(self):
        raise NotImplementedError

    def close(self):
        raise NotImplementedError

class ExcelWeekLongWriter(WeekLongWriter):
    """Writes a WeekLongReadingPlan as an Excel spreadsheet to disk.
    """
    def __init__(self, outfile=None, format_outfile=True):
        outfile = os.path.expanduser(outfile)+'.xlsx'
        super(ExcelWeekLongWriter, self).__init__(outfile, format_outfile)

    def write_header(self, header_str):
        self.worksheet.write(cell(self.column, self.row), header_str, self.bold)

    def write_data(self, data_str):
        self.worksheet.write(cell(self.column, self.row), data_str)

    def open(self):
        if os.path.exists(self.outfile):
            os.remove(self.outfile)
        self.workbook = xlsxwriter.Workbook(self.outfile)
        self.worksheet = self.workbook.add_worksheet()
        self.bold = self.workbook.add_format({'bold': self.format_outfile})
        if self.format_outfile:
            self.worksheet.set_landscape()
            self.workbook.formats[DEFAULT_CELL].set_font_size(10)
            self.bold.set_font_size(10)

    def close(self):
        if self.format_outfile:
            self.worksheet.set_v_pagebreaks([1 + i * self.row_limit for i in range(1, self.page)])
        self.workbook.close()

class CsvWeekLongWriter(WeekLongWriter):
    """Writes a WeekLongReadingPlan as a CSV to disk.
    """
    def __init__(self, outfile=None, format_outfile=False):
        outfile = os.path.expanduser(outfile)+'.csv'
        super(CsvWeekLongWriter, self).__init__(outfile, format_outfile)
        self.rows = []

    def write_header(self, header_str):
        self.write(header_str)

    def write_data(self, data_str):
        self.write(data_str)

    def write(self, cell_string):
        while len(self.rows) < self.row:
            self.rows.append([])
        self.rows[self.row-1].extend([cell_string])

    def open(self):
        if os.path.exists(self.outfile):
            os.remove(self.outfile)
        self.readingplan = open(os.path.expanduser(self.outfile), 'w')
        self.csv_writer = csv.writer(self.readingplan, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

    def close(self):
        self.csv_writer.writerows(self.rows)
        self.readingplan.close()

class ReadingPlan(object):
    """A minimalist reading plan.
    """
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

    @property
    def formatted_date_range(self):
        fdr = '%s %d' % (self.from_date.strftime('%b'), self.from_date.day)
        if self.from_date != self.to_date:
            fdr += ' - '
            if self.from_date.month != self.to_date.month:
                fdr += '%s ' % self.to_date.strftime('%b')
            fdr += str(self.to_date.day)
        return fdr

class WeekLongReadingPlan(ReadingPlan):
    """A reading plan based off of 1 week of reading.
    """
    def __init__(self, from_date=None, to_date=None, startpage=None, endpage=None, frequency=5):
        super(WeekLongReadingPlan, self).__init__(from_date, to_date, startpage, endpage, frequency)
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
        cur_date = self.from_date
        while not (cur_date > self.to_date):
            self.days.append(ReadingPlan(from_date=cur_date, to_date=cur_date))
            cur_date += timedelta(days=1)

class BookReadingPlan(ReadingPlan):
    """A reading plan based off multiple weeks of reading.
    """
    def __init__(self, from_date=None, to_date=None, startpage=None, endpage=None, frequency=5):
        super(BookReadingPlan, self).__init__(from_date, to_date, startpage, endpage, frequency)
        self.weeks = []
        self.populate_weeks()

    def write_excel(self, outdir, format_outfile=True):
        self._write(ExcelWeekLongWriter, outdir, format_outfile)

    def write_csv(self, outdir, format_outfile=False):
        self._write(CsvWeekLongWriter, outdir, format_outfile)

    def _write(self, writer_class, outdir, format_outfile):
        outfile = os.path.join(outdir, OUT_FILENAME)
        weekly_writer = writer_class(outfile, format_outfile)
        for week in self.weeks:
            weekly_writer.write_week(week)
        weekly_writer.write_weekly_summary(self.weeks)
        weekly_writer.close()

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
        cur_date = self.from_date
        first_week_day = self.from_date
        while not (cur_date > self.to_date):
            if cur_date.weekday() == 6:
                last_week_day = cur_date - timedelta(days=1)
                self.weeks.append(WeekLongReadingPlan(from_date=first_week_day, to_date=last_week_day, frequency=self.frequency))
                first_week_day = cur_date
            cur_date += timedelta(days=1)
        if last_week_day != cur_date:
            last_week_day = cur_date - timedelta(days=1)
            self.weeks.append(WeekLongReadingPlan(from_date=first_week_day, to_date=last_week_day, frequency=self.frequency))

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

def num_to_word(num):
    if 0 <= num <= 19:
        return num2words1[num]
    elif 20 <= num <= 99:
        tens, below_ten = divmod(num, 10)
        return num2words2[tens - 2] + '-' + num2words1[below_ten] if below_ten else num2words2[tens - 2]
    else:
        raise NotImplementedError('Number out of implemented range of numbers.')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--from-date', required=True)
    parser.add_argument('--to-date', required=True)
    parser.add_argument('--start-page', required=True, type=int)
    parser.add_argument('--end-page', required=True, type=int)
    parser.add_argument('--frequency', type=int, default=5)
    parser.add_argument('--outdir', default='~/Desktop/')
    parser.add_argument('--excel', action='store_true')
    parser.add_argument('--csv', action='store_true')
    (options, args) = parser.parse_known_args()

    from_date = datetime.strptime(options.from_date, '%Y%m%d')
    to_date = datetime.strptime(options.to_date, '%Y%m%d')
    cur_date = from_date

    book_reading_plan = BookReadingPlan(from_date=from_date, 
                                          to_date=to_date, 
                                          startpage=options.start_page, 
                                          endpage=options.end_page,
                                          frequency=options.frequency)

    if int(options.excel) + int(options.csv) < 1:
        raise Exception('No reading plan file format was specified.')
    if options.excel:
        book_reading_plan.write_excel(options.outdir)
    if options.csv:
        book_reading_plan.write_csv(options.outdir)