Amazon & Waterstones Synopsis Scraper

Based on the Heroku Django Starter Template
https://github.com/heroku/heroku-django-template

Deployed to Heroku here;
https://dashboard.heroku.com/apps/wellreadscraper

It provides a single service, at the root of the project, that is called at runtime by the WellRead website;
https://wellreadscraper.herokuapp.com/

This service takes the following request parameters;
url: The URL for the book at Amazon, e.g. http://www.amazon.co.uk/DanTDM-Trayaurus-Enchanted-Crystal/dp/1409168395
asin: The Amazon book ID, e.g. 1409168395. We pass this in seperately in case it can't be extracted from the Amazon URL - it's the primary ID of a book on WellRead.
isbn: The book's 13 digit ISBN code, e.g. 9781409168393. This is used to dynamically generate the Waterstones URL.

Running locally;

remember to source your local environment variables
source init.sh

python manage.py runserver
