import os
from random import randint
import flask
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from application import app,application

path_prefix = os.environ['REQUESTS_PATHNAME_PREFIX']

from apps import common, logs, annual_min, cumulative_gdd, hardiness

server = flask.Flask(__name__)
#app.config.requests_pathname_prefix = os.environ['REQUESTS_PATHNAME_PREFIX']
#app = dash.Dash(external_scripts = external_scripts, server=server, requests_pathname_prefix=os.environ['REQUESTS_PATHNAME_PREFIX'])
server.secret_key = os.environ.get("secret_key", str(randint(0, 1000000)))

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    common.header(),
    dcc.Tabs(
        id="tabs", 
        value='tab-1', 
        children=[
            dcc.Tab(label='Growing Season', value='tab-1'),
            dcc.Tab(label='Annual Minimums', value='tab-2'),
            dcc.Tab(label='Growing Degree Days', value='tab-3'),
            dcc.Tab(label='Hardiness Zones', value='tab-4'),
        ]
    ),
    html.Div(id='page-content'),
    common.footer()
])
app.title = 'Alaska Garden Helper'

@app.callback(Output('page-content', 'children'),
		[
			Input('url', 'pathname'),
			Input('tabs', 'value')
		]
	)
def display_page(pathname, tabs):
    print(tabs)
    if pathname is None:
        return 'Loading...'
    if tabs == 'tab-1':
        return logs.layout
    if tabs == 'tab-2':
        return annual_min.layout
    if tabs == 'tab-3':
        return cumulative_gdd.layout
    if tabs == 'tab-4':
        return hardiness.layout
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
