# python native libs
from reading_plan.writers import BookReadingPlanWriter, OUT_FILENAME
from reading_plan.plans import BookReadingPlan
from datetime import datetime
import os
import sys
import io

# flask libs
from flask import Flask, render_template, send_file, request, abort

# custom libs
dirname = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(dirname, 'reading_plan'))

# globals
NUMBER = 0
OUTDIR = '/tmp'  # https://cloud.google.com/appengine/docs/standard/python3/using-temp-files

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('index.html')


@app.errorhandler(400)
def error(e):
    error_message = str(e).replace('\n', '<br>').replace('\t', '&nbsp;'*4)
    return render_template('error.html', error=error_message)


@app.route('/generateReadingPlan', methods=['POST'])
def generate_reading_plan():
    try:
        start_date = datetime.strptime(request.form['start_date'], '%m/%d/%Y')
        end_date = datetime.strptime(request.form['end_date'], '%m/%d/%Y')
        start_page = int(request.form['start_page'])
        end_page = int(request.form['end_page'])
        frequency = int(request.form['frequency'][NUMBER])
        book_name = request.form['book_name']
        book_reading_plan = BookReadingPlan(start_date=start_date,
                                            end_date=end_date,
                                            startpage=start_page,
                                            endpage=end_page,
                                            frequency=frequency,
                                            name=book_name)
        output_file_type = request.form['output_file_type'].lower()
        format_outfile = 'format_outfile' in request.form
        writer = BookReadingPlanWriter(book_reading_plan)
        if 'csv' in output_file_type:
            mimetype = 'text/csv'
            outfile_path = writer.write_csv(
                OUTDIR, format_outfile=format_outfile)
        elif 'excel' in output_file_type:
            mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            outfile_path = writer.write_excel(
                OUTDIR, format_outfile=format_outfile)
        mem_outfile = disk_to_memory(outfile_path)
        return send_file(mem_outfile,
                         mimetype=mimetype,
                         attachment_filename='%s%s' % (
                             OUT_FILENAME, os.path.splitext(outfile_path)[1]),
                         as_attachment=True)
    except Exception as e:
        abort(400, e)


def disk_to_memory(disk_path):
    mem_file = io.BytesIO()
    with open(disk_path, 'rb') as f:
        mem_file.write(f.read())
    mem_file.seek(0)
    os.remove(disk_path)
    return mem_file


if __name__ == "__main__":
    app.run(debug=True)
