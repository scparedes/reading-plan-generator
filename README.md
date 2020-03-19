
# reading-plan-generator
Generates a reading plan as an Excel or CSV spreadsheet based on:
* a start date,
* an end date,
* a start page, and
* an end page.

#### Recommendations and Reminders
The Excel output format is recommended for easy-to-look at spreadsheet results. Excel version 16 is recommnded for your version of Excel.
There is a limit on the length of reading plans to protect against inundating the Google App Engine.  The limit is set to 3 years in the Web App.
There is no form/input validation implemented in the Web App, so failure to enter expected types of values in specific fields will render ugly stacktraces for end-users.

## Using the Web App
Plans can be generated using the Google App Engine's hosting of the app [here](here).
This app runs in the us-east4 (Ashburn, Northern Virginia, USA) region.

## Using the CLI
Plans can be generated using a console by running the `create_plan.py` script inside this repo:
```
$ pwd
reading-plan
$ cd src/reading_plan
$ python create_plan.py --start-date=20200101 --end-date=20201231 --start-page=1 --end-page=1000 --frequency=5 --excel
```
## Why?
I created this app because I've experience incredible success with an N-day reading strategy for years.  With plans like these, I've been able to tackle seemingly impossible reads but reading one day at time consistently over a long period of time.  Textbooks, religious texts, even encyclopedia's become reasonable to consume in their entirety when you use an N-day reading plan.  My personal preference is a frequency of 5 days per week (5-day reading plan).

Also, I've developed in Python2.7 for years but have yet to develop anything in Python 3, so this was a good exercise to receive some Python3 exposure.