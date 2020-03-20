

# reading-plan-generator
Generates a reading plan as an Excel or CSV spreadsheet based on:
* a start date,
* an end date,
* a start page, and
* an end page.

#### Recommendations and Reminders
* To view your reading plan as it will be printed, go to 'View' -> 'Page Layout' in your Excel options.
* Excel version 16 is recommended for your version of Excel.
* There is a limit on the length of reading plans to protect against inundating the Google App Engine.  The limit is set to 3 years in the Web App.
* There is no form/input validation implemented in the Web App, so failure to enter expected types of values in specific fields will render ugly stacktraces for end-users.

## Using the Web App
Plans can be generated using the Google App Engine's hosting of the app [here](https://reading-plan-generator.appspot.com/).
This app runs in the us-east4 (Ashburn, Northern Virginia, USA) region.

## Using the CLI
Plans can be generated using a console by running the `create_plan.py` script inside this repo:
```
$ pwd
reading-plan
$ cd src/reading_plan
$ python create_plan.py --help
```
## Why?
I created this app because I've experienced incredible success with an N-day reading strategy for years. The 5-day reading plan has helped me read thousands of dense pages of literature that I would have never had the courage to tackle beforehand.  Textbooks, religious texts, novels, anything. With these plans you can tackle any book over any time frame you desire.

Also, I've developed in Python 2.7 for years but have yet to develop anything in Python 3, so this was a good exercise to receive some Python 3 exposure.
