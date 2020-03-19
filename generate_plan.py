# native python libs
from datetime import datetime
import argparse

# custom libs
from reading_plans import BookReadingPlan
from writers import BookReadingPlanWriter

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

    if int(options.excel) + int(options.csv) < 1:
        raise Exception('No reading plan file format was specified.')

    from_date = datetime.strptime(options.from_date, '%Y%m%d')
    to_date = datetime.strptime(options.to_date, '%Y%m%d')
    book_reading_plan = BookReadingPlan(from_date=from_date, 
                                          to_date=to_date, 
                                          startpage=options.start_page, 
                                          endpage=options.end_page,
                                          frequency=options.frequency)

    plan_writer = BookReadingPlanWriter(book_reading_plan)
    if options.excel:
        plan_writer.write_excel(options.outdir)
    if options.csv:
        plan_writer.write_csv(options.outdir)