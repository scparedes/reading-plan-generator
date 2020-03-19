# python native libs
from datetime import datetime
import os
import sys

# flask libs
from flask import Flask, render_template, send_file, request

# custom libs
dirname = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(dirname, 'reading_plan'))
from reading_plan.plans import BookReadingPlan
from reading_plan.writers import BookReadingPlanWriter

# globals
NUMBER = 0
OUTDIR = '~/Desktop'

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generateReadingPlan', methods=['POST'])
def generate_reading_plan():
    # import pdb;pdb.set_trace()
    start_date = datetime.strptime(request.form['start_date'], '%m/%d/%Y')
    end_date = datetime.strptime(request.form['end_date'], '%m/%d/%Y')
    start_page = int(request.form['start_page'])
    end_page = int(request.form['end_page'])
    frequency = int(request.form['frequency'][NUMBER])
    book_reading_plan = BookReadingPlan(start_date=start_date,
                                        end_date=end_date,
                                        startpage=start_page,
                                        endpage=end_page,
                                        frequency=frequency)

    output_file_type = request.form['output_file_type'].lower()
    format_outfile = request.form['format_outfile'] == 'on'
    writer = BookReadingPlanWriter(book_reading_plan)
    if 'csv' in output_file_type:
        mimetype = 'text/csv'
        outfile = writer.write_csv(OUTDIR, format_outfile=format_outfile)
    elif 'excel' in output_file_type:
        mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        outfile = writer.write_excel(OUTDIR, format_outfile=format_outfile)
    return send_file(outfile,
                     mimetype=mimetype,
                     attachment_filename=os.path.basename(outfile),
                     as_attachment=True)
    
if __name__ == "__main__":
    app.run(debug=True)