from datetime import datetime, timedelta, date
import csv
import argparse

def split(a, n):
    k, m = divmod(len(a), n)
    return [a[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in xrange(n)]

if __name__ == '__main__':
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--from-date')
    parser.add_argument('--to-date')
    parser.add_argument('--start-page')
    parser.add_argument('--end-page')
    (options,args) = parser.parse_known_args()

    from_date = datetime.strptime(options.from_date, '%Y%m%d')
    to_date = datetime.strptime(options.to_date, '%Y%m%d')
    cur_date = from_date

    pages = [i for i in xrange(int(options.start_page), int(options.end_page))]
    pages += [int(options.end_page)]
    daygenerator = (from_date + timedelta(x + 1) for x in xrange((to_date - from_date).days))
    num_weekdays = sum(1 for day in daygenerator if day.weekday() < 5)
    print num_weekdays
    # reading_plan_size = 5
    # page_list_per_weekday = [pages[i:i + reading_plan_size] for i in xrange(0, len(pages), reading_plan_size)]
    page_list_per_weekday = split(pages, num_weekdays)

    with open('readingplan.csv', 'w') as readingplan:
        week_last_seen = cur_date.date().isocalendar()[1]
        readingplan.write('Week %d\n' % week_last_seen) # Initial week write
        csv_writer = csv.writer(readingplan, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        while not (cur_date > to_date):
            calendar_week = cur_date.date().isocalendar()[1]
            if week_last_seen != calendar_week:
                readingplan.write('Week %d\n' % calendar_week)
                week_last_seen = cur_date.date().isocalendar()[1]
            if not cur_date.date().weekday() >= 5:
                try:
                    page_list = page_list_per_weekday.pop(0)
                except IndexError:
                    break
                row_data = page_list[0] == page_list[-1] and '%d' % page_list[0] or '%d-%d' % (page_list[0], page_list[-1])
                csv_writer.writerow(['o  '+row_data])
                # readingplan.write(row_data+'\n')
            cur_date += timedelta(days=1)

    print 'done'