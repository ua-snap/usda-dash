import os
from random import randint
import flask
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from application import app,application
from apps import logs, annual_min, cumulative_gdd

server = flask.Flask(__name__)
#app.config.requests_pathname_prefix = os.environ['REQUESTS_PATHNAME_PREFIX']
#app = dash.Dash(external_scripts = external_scripts, server=server, requests_pathname_prefix=os.environ['REQUESTS_PATHNAME_PREFIX'])
server.secret_key = os.environ.get("secret_key", str(randint(0, 1000000)))

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname is None:
        return 'Loading...'
    if pathname == '/':
         return logs.layout
    elif pathname == '/logs':
         return logs.layout
    elif pathname == '/annual_min':
         return annual_min.layout
    elif pathname == '/cumulative_gdd':
         return cumulative_gdd.layout
    else:
        return '404'

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    debug = os.environ.get("DEBUG", True)
    #app.server.run(debug=debug, port=port)
    app.server.run(debug=debug, port=port, threaded=True)
