# native python libs
import os
import csv
import string
import calendar
from math import ceil
import uuid

# 3rd party libraries
import xlsxwriter

# globals
from common import WEEKDAYS, START_OF_WEEK, week_of_month
MONTHS = calendar.month_name
PAGE_ROW_LIMIT = 35
PAGE_COLUMN_LIMIT = 16
COLUMN_INCREMENT = 2
EXCEL_COLUMNS = dict(enumerate(string.ascii_uppercase, 1))
DEFAULT_CELL = 0
OUT_FILENAME = 'reading-plan'


class BookReadingPlanWriter(object):
    def __init__(self, book_reading_plan):
        self.plan = book_reading_plan

    def write_excel(self, outdir, format_outfile=True):
        return self._write(ExcelWeekLongWriter, outdir, format_outfile, self.plan.name)

    def write_csv(self, outdir, format_outfile=False):
        return self._write(CsvWeekLongWriter, outdir, format_outfile)

    def _write(self, writer_class, outdir, format_outfile, plan_name=None):
        outfile = os.path.join(outdir, OUT_FILENAME)
        if outdir == '/tmp':
            outfile += str(uuid.uuid4())
        writer_args = [outfile, format_outfile]
        if plan_name:
            writer_args += [plan_name]
        weekly_writer = writer_class(*writer_args)
        for week in self.plan.weeks:
            weekly_writer.write_week(week)
        weekly_writer.write_weekly_summary(self.plan.weeks)
        weekly_writer.close()
        return weekly_writer.outfile

def post_increment_row(func):
    def wrapper(*args, **kwargs):
        func(*args, **kwargs)
        args[0].increment_row()
    return wrapper

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
        self._weeks_seen = 0

    def write_week(self, week):
        self._weeks_seen += 1
        if not week.days:
            return
        month_name = MONTHS[week.start_date.month]
        if self.format_outfile:
            self.select_column_and_page(len(week.days))
        # TODO: Correctly calculate the first weekday `self.write_header('%s, week %d' % (month_name, week_of_month(week.start_date)))`
        self.write_header('Week %d' % self._weeks_seen)
        for day in week.days:
            if not day.startpage:
                continue
            if day.startpage == day.endpage:
                self.write_data('o  ' + '%d' % (day.startpage))
            else:
                self.write_data('o  ' + '%d-%d' % (day.startpage, day.endpage))

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
        if self.format_outfile:
            while not self.is_pointing_to_new_column:
                self.increment_row()
                self.select_column_and_page(1)
            self.column_increment += 2
        self.write_header('Week No.')
        # TODO: Correctly calculate the first weekday `first_weekday = weeks[0].start_date.weekday()`
        #                                             `start_week_offset = int(first_weekday == START_OF_WEEK)``
        start_week_offset = 1
        for overall_week_number, week in enumerate(weeks, start_week_offset):
            if not week.days:
                continue
            if self.format_outfile:
                self.select_column_and_page(1)
            weekly_summary_row = ('___ %s' % num_to_word(overall_week_number)).ljust(20, '.') + week.formatted_date_range
            self.write_data(weekly_summary_row)

    @property
    def is_pointing_to_new_column(self):
        return (self.row - self.row_limit) % self.row_limit == 1

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
    def __init__(self, outfile=None, format_outfile=True, plan_name=None):
        outfile = os.path.expanduser(outfile)+'.xlsx'
        self.plan_name = plan_name
        super(ExcelWeekLongWriter, self).__init__(outfile, format_outfile)

    @post_increment_row
    def write_header(self, header_str):
        self.worksheet.write(cell(self.column, self.row), header_str, self.bold)

    @post_increment_row
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
            self.worksheet.set_margins(left=.25, right=.25, top=.75, bottom=.75)
            self.worksheet.set_header('&C&"Calibri,Bold"&18%s Reading Plan' % self.plan_name)
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

    @post_increment_row
    def write_header(self, header_str):
        self.write(header_str)

    @post_increment_row
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

def cell(column, row):
    return '%s%s' % (EXCEL_COLUMNS[column], row)

BASE_NUMBERS = {0:'Zero', 1: 'One', 2: 'Two', 3: 'Three', 4: 'Four', 5: 'Five', \
                6: 'Six', 7: 'Seven', 8: 'Eight', 9: 'Nine', 10: 'Ten', \
                11: 'Eleven', 12: 'Twelve', 13: 'Thirteen', 14: 'Fourteen', \
                15: 'Fifteen', 16: 'Sixteen', 17: 'Seventeen', 18: 'Eighteen', 19: 'Nineteen'}
TENS_NUMBERS = ['Twenty', 'Thirty', 'Forty', 'Fifty', 'Sixty', 'Seventy', 'Eighty', 'Ninety']

def num_to_word(num):
    if 0 <= num <= 19:
        return BASE_NUMBERS[num]
    elif 20 <= num <= 99:
        tens, below_ten = divmod(num, 10)
        return TENS_NUMBERS[tens - 2] + '-' + BASE_NUMBERS[below_ten] if below_ten else TENS_NUMBERS[tens - 2]
    else:
        raise NotImplementedError('Number out of implemented range of numbers.')