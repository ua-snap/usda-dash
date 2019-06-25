import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from application import app
from apps import logs, annual_min, cumulative_gdd

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
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
    app.run_server(debug=False, port=8050)
    #app.run_server(debug=True, port=8050)
