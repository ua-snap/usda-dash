import os
from random import randint
import flask
import dash

#server = flask.Flask(__name__)
#app.config.requests_pathname_prefix = os.environ['REQUESTS_PATHNAME_PREFIX']
#app = dash.Dash(external_scripts = external_scripts, server=server, requests_pathname_prefix=os.environ['REQUESTS_PATHNAME_PREFIX'])
#server.secret_key = os.environ.get("secret_key", str(randint(0, 1000000)))
app = dash.Dash(__name__)
#app = dash.Dash(__name__,server=server)

# AWS Elastic Beanstalk looks for application by default,
# if this variable (application) isn't set you will get a WSGI error.
app.config['suppress_callback_exceptions']=True
application = app.server


