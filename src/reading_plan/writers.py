# native python libs
import os
import csv
import string
import calendar
from typing import Callable, List
import uuid

import xlsxwriter

from .plans import BookReadingPlan, ReadingPlan


MONTHS = calendar.month_name
PAGE_ROW_LIMIT = 35
PAGE_COLUMN_LIMIT = 16
BLANK_COLUMNS = 2
EXCEL_COLUMNS = dict(enumerate(string.ascii_uppercase, 1))
DEFAULT_CELL = 0
OUT_FILENAME = 'reading-plan'


class BookReadingPlanWriter():
    """Writes a BookReadingPlan to disk.

    Args:
        book_reading_plan: A reading plan for a book.
    """
    def __init__(self, book_reading_plan: BookReadingPlan):
        self.plan = book_reading_plan

    def write_excel(self, outdir: str, format_outfile: bool = True):
        """Writes the reading plan as an excel file to disk.

        Args:
            outdir: The directory to which to write the reading plan.
            format_outfile: Whether to attempt to format the plan (for
                printer-friendly results).

        Returns:
            The path to the excel reading plan.
        """
        return self._write(
            ExcelWeekLongWriter, outdir, format_outfile, self.plan.name)

    def write_csv(self, outdir: str, format_outfile: bool = True):
        """Writes the reading plan as a CSV file to disk.

        Args:
            outdir: The directory to which to write the reading plan.
            format_outfile: Whether to attempt to format the plan (for
                printer-friendly results).

        Returns:
            The path to the CSV reading plan.
        """
        return self._write(CsvWeekLongWriter, outdir, format_outfile)

    def _write(self,
               writer_class, # TODO: Type hint with ReadingPlanWriter.
               outdir: str,
               format_outfile: bool = True,
               plan_name: str = None) -> str:
        """Writes the reading plan to disk.

        Args:
            writer_class: The type of the reading plan writer.
            outdir: The directory to which to write the reading plan.
            format_outfile: Whether to attempt to format the plan (for
                printer-friendly results).
            plan_name: The name of the reading plan.

        Returns:
            The path to the excel reading plan.
        """
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


def post_increment_row(func: Callable):
    """A decorator for incrementing the row of a ReadingPlanWriter."""
    def wrapper(*args, **kwargs):
        func(*args, **kwargs)
        reading_plan_writer = args[0]
        reading_plan_writer.increment_row()
    return wrapper


class ReadingPlanWriter():
    """Writes a ReadingPlan to disk.

    Args:
        outfile: The path to which to write the reading plan.
        format_outfile: Whether to attempt to format the plan (for
            printer-friendly results).
        row_limit: The max length of rows before wrapping to the next column.
        column_limit: The max width of columns before wrapping to the next row.
        blank_columns: The number of blank columns to put in between columns.
    """
    def __init__(self,
                 outfile: str = None,
                 format_outfile: bool = True,
                 row_limit: int = PAGE_ROW_LIMIT,
                 column_limit: int = PAGE_COLUMN_LIMIT,
                 blank_columns: int = BLANK_COLUMNS):
        self.outfile = outfile
        self.format_outfile = format_outfile
        self.open()
        self.page = 0
        self.row = 1
        self.column = 1
        self.row_limit = row_limit
        self.column_limit = column_limit
        self.blank_columns = blank_columns
        self.column_overflow_buffer = self.column_limit - 1
        self._weeks_seen = 0

    def write_week(self, week: ReadingPlan):
        """Write a week of reading plan data to disk.

        Args:
            week: A week's worth of reading.
        """

        self._weeks_seen += 1
        if not week.days:
            return
        month_name = MONTHS[week.start_date.month]
        if self.format_outfile:
            self.select_column_and_page(len(week.days))
        # TODO: Correctly calculate the first weekday `self.write_header('%s, week %d' % (month_name, week_of_month(week.start_date)))`
        self.write_header('Week %d' % self._weeks_seen)
        for day in week.days:
            if not day.start_page:
                continue
            if day.start_page == day.end_page:
                self.write_data('o  ' + '%d' % (day.start_page))
            else:
                self.write_data('o  ' + '%d-%d' % (day.start_page, day.end_page))

    def select_column_and_page(self, num_additional_rows: int):
        """Updater the writer head to point to a column on a page.

        The column and page are calculated based on will fit

        Args:
            num_additional_rows: The number of rows that will be written.
        """
        if self.additional_rows_will_fit_on_current_page(num_additional_rows):
            self.column += self.blank_columns
            self.row = 1 + self.page * self.row_limit
            if self.column > self.column_overflow_buffer:
                self.column = 1
                self.page += 1
                self.row = 1 + self.page * self.row_limit

    def additional_rows_will_fit_on_current_page(self, num_rows: int) -> bool:
        """Whether the number of rows that are proposed to be written will fit.

        Args:
            num_rows: The number of rows that are proposed to be written.
        """
        return (num_rows + 1 + (self.row -
                                self.page * self.row_limit)
                > self.row_limit)

    def increment_row(self):
        """Updates the writer head to point to the next row"""
        self.row += 1

    def write_weekly_summary(self, weeks: List[ReadingPlan]):
        """Writes a summary of each week of reading.

        Args:
            weeks: A list of reading plans.
        """
        if self.format_outfile:
            while not self.has_reached_row_limit:
                self.increment_row()
                self.select_column_and_page(1)
            self.blank_columns += 2
        self.write_header('Week No.')
        # TODO: Correctly calculate the first weekday `first_weekday = weeks[0].start_date.weekday()`
        #                                             `start_week_offset = int(first_weekday == START_OF_WEEK)``
        start_week_offset = 1
        for week_number, week in enumerate(weeks, start_week_offset):
            if not week.days:
                continue
            if self.format_outfile:
                self.select_column_and_page(1)
            weekly_summary_row = ('___ %s' % num_to_word(week_number)
                                  ).ljust(20, '.') + week.formatted_date_range
            self.write_data(weekly_summary_row)

    @property
    def has_reached_row_limit(self) -> bool:
        """Whether the writer head has reached the row limit."""
        return (self.row - self.row_limit) % self.row_limit == 1

    def write_header(self, header: str):
        """Write the header to disk.

        Args:
            The spreadsheet header.
        """
        raise NotImplementedError

    def write_data(self, data: str):
        """Write the data to disk.

        Args:
            The data to write to a cell.
        """
        raise NotImplementedError

    def open(self):
        """Opens the writer."""
        raise NotImplementedError

    def close(self):
        """Closes the writer."""
        raise NotImplementedError


class ExcelWeekLongWriter(ReadingPlanWriter):
    """Writes a WeekLongReadingPlan as an Excel spreadsheet to disk.

    Args:
        outfile: The path to which to write the reading plan.
        format_outfile: Whether to attempt to format the plan (for
            printer-friendly results).
        plan_name: The name of the reading plan.
    """

    def __init__(self,
                 outfile: str = None,
                 format_outfile: bool = True,
                 plan_name: str = None):
        outfile = os.path.expanduser(outfile)+'.xlsx'
        self.plan_name = plan_name
        super(ExcelWeekLongWriter, self).__init__(outfile, format_outfile)

    @post_increment_row
    def write_header(self, header: str):
        self.worksheet.write(self.to_coordinate(self.column, self.row),
                             header,
                             self.bold)

    @post_increment_row
    def write_data(self, data: str):
        self.worksheet.write(self.to_coordinate(self.column, self.row),
                             data)

    def to_coordinate(self, column: int, row: int):
        """Convert a column and row into the excel cell coordinate format.

        Args:
            column: A column number
            row: A row number.

        Returns:
            An excel cell coordinate.
        """
        return '%s%s' % (EXCEL_COLUMNS[column], row)

    def open(self):
        if os.path.exists(self.outfile):
            os.remove(self.outfile)
        self.workbook = xlsxwriter.Workbook(self.outfile)
        self.worksheet = self.workbook.add_worksheet()
        self.bold = self.workbook.add_format({'bold': self.format_outfile})
        if self.format_outfile:
            self.worksheet.set_landscape()
            self.worksheet.set_margins(
                left=.25, right=.25, top=.75, bottom=.75)
            self.worksheet.set_header(
                '&C&"Calibri,Bold"&18%s Reading Plan' % self.plan_name)
            self.workbook.formats[DEFAULT_CELL].set_font_size(10)
            self.bold.set_font_size(10)

    def close(self):
        if self.format_outfile:
            self.worksheet.set_v_pagebreaks(
                [1 + i * self.row_limit for i in range(1, self.page)])
        self.workbook.close()


class CsvWeekLongWriter(ReadingPlanWriter):
    """Writes a WeekLongReadingPlan as a CSV to disk.
    """

    def __init__(self, outfile: str = None, format_outfile: bool = False):
        outfile = os.path.expanduser(outfile)+'.csv'
        super(CsvWeekLongWriter, self).__init__(outfile, format_outfile)
        self.rows = []

    @post_increment_row
    def write_header(self, header: str):
        self.write(header)

    @post_increment_row
    def write_data(self, data: str):
        self.write(data)

    def write(self, cell: str):
        while len(self.rows) < self.row:
            self.rows.append([])
        self.rows[self.row-1].extend([cell])

    def open(self):
        if os.path.exists(self.outfile):
            os.remove(self.outfile)
        self.readingplan = open(os.path.expanduser(self.outfile), 'w')
        self.csv_writer = csv.writer(self.readingplan,
                                     delimiter=',',
                                     quotechar='"',
                                     quoting=csv.QUOTE_MINIMAL)

    def close(self):
        self.csv_writer.writerows(self.rows)
        self.readingplan.close()


def num_to_word(num: int) -> str:
    """Converts a number to a word.

    The number must be between 1 and 999.

    Args:
        num: A number to convert to a word.

    Returns:
        A word representation of a number.
    """
    if num > 999 or num < 0:
        raise NotImplementedError(
            'Number out of implemented range of numbers.')
    if num > 99:
        hundreds, tens_and_ones = divmod(num, 100)
        return BASE_NUMBERS[hundreds] + ' Hundred ' + num_to_word(tens_and_ones)
    if num > 19:
        tens, ones = divmod(num, 10)
        return TENS_NUMBERS[tens] + ('-' + BASE_NUMBERS[ones] if ones else '')
    return BASE_NUMBERS[num]


BASE_NUMBERS = {0: '', 1: 'One', 2: 'Two', 3: 'Three', 4: 'Four', 5: 'Five',
                6: 'Six', 7: 'Seven', 8: 'Eight', 9: 'Nine', 10: 'Ten',
                11: 'Eleven', 12: 'Twelve', 13: 'Thirteen', 14: 'Fourteen',
                15: 'Fifteen', 16: 'Sixteen', 17: 'Seventeen', 18: 'Eighteen',
                19: 'Nineteen'}
TENS_NUMBERS = ['', '', 'Twenty', 'Thirty', 'Forty', 'Fifty',
                'Sixty', 'Seventy', 'Eighty', 'Ninety']
