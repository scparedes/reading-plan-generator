"""Creates a n-day reading plan for a book.
"""
# pylint: disable=C0103
import argparse
from datetime import datetime


from plans import BookReadingPlan
from writers import BookReadingPlanWriter


if __name__ == '__main__':
    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument('--start-date', required=True)
    parser.add_argument('--end-date', required=True)
    parser.add_argument('--start-page', required=True, type=int)
    parser.add_argument('--end-page', required=True, type=int)
    parser.add_argument('--frequency', type=int, default=5)
    parser.add_argument('--book-name', default='')
    parser.add_argument('--outdir', default='~/Desktop/')
    parser.add_argument('--excel', action='store_true')
    parser.add_argument('--csv', action='store_true')
    parser.add_argument('--format-outfile', action='store_true')
    (options, args) = parser.parse_known_args()

    if int(options.excel) + int(options.csv) < 1:
        raise Exception('No reading plan file format was specified.')

    start_date = datetime.strptime(options.start_date, '%Y%m%d')
    end_date = datetime.strptime(options.end_date, '%Y%m%d')
    book_reading_plan = BookReadingPlan(start_date=start_date,
                                        end_date=end_date,
                                        start_page=options.start_page,
                                        end_page=options.end_page,
                                        num_times_to_read=options.frequency,
                                        name=options.book_name)

    plan_writer = BookReadingPlanWriter(book_reading_plan)
    if options.excel:
        plan_writer.write_excel(options.outdir,
                                format_outfile=options.format_outfile)
    if options.csv:
        if options.book_name:
            print('WARNING: CSV files do not support headers, so your book ' +
                  'name will not be integrated as a header into your ' +
                  'spreadsheet.')
        plan_writer.write_csv(
            options.outdir, format_outfile=options.format_outfile)
