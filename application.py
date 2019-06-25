import os
import dash

external_scripts = ['https://code.jquery.com/jquery-3.3.1.min.js']

app = dash.Dash(external_scripts = external_scripts)
app.config.requests_pathname_prefix = os.environ['REQUESTS_PATHNAME_PREFIX']

# AWS Elastic Beanstalk looks for application by default,
# if this variable (application) isn't set you will get a WSGI error.
application = app.server

app.config['suppress_callback_exceptions']=True
