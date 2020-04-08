import os
from random import randint
import flask
import dash

app = dash.Dash(__name__)
# app = dash.Dash(__name__,server=server)

# AWS Elastic Beanstalk looks for application by default,
# if this variable (application) isn't set you will get a WSGI error.
app.config["suppress_callback_exceptions"] = True
application = app.server
