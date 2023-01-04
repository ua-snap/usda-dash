# Alaska Garden Helper

This application highlights a number of features about changes growing seasons under projected climate data, showing:

* Length of Growing Season above N degrees
* Minimum Annual Temperatures by 30 year period
* Cumulative Growing Degrees
* Alaska Hardiness Zone Maps

To install the app, use the following command:

`pipenv install`

This app can be run locally with the following commands:

`export DASH_REQUESTS_PATHNAME_PREFIX=''`

`pipenv run python index.py`

### Note
It may be necessary to comment out the following line in index.py for local use:

`app.config.requests_pathname_prefix = os.environ['REQUESTS_PATHNAME_PREFIX'`

Be sure to uncomment this line before deploying to AWS or the deployed app may not function.
