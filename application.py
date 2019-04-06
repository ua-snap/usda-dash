'''
Template for SNAP Dash apps.
'''
import os
import json
import plotly.graph_objs as go
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_dangerously_set_inner_html as ddsih
import pandas as pd
import geopandas as gpd
import numpy as np
from dash.dependencies import Input, Output, State
import visdcc

external_scripts = ['https://code.jquery.com/jquery-3.3.1.min.js']

app = dash.Dash(external_scripts = external_scripts)

# AWS Elastic Beanstalk looks for application by default,
# if this variable (application) isn't set you will get a WSGI error.
application = app.server

app.title = 'SNAP - USDA Garden Helper'

mapbox_access_token = os.environ['MAPBOX_ACCESS_TOKEN']
path_prefix = os.environ['REQUESTS_PATHNAME_PREFIX']
communities = gpd.read_file('MainCommunities_4326.json')

header_section = html.Div(
    className='header',
    children=[
        html.Div(
            className='container',
            children=[
                html.Div(
                    className='section',
                    children=[
                        html.Div(
                            className='columns',
                            children=[
                                html.Div(
                                    className='header--logo',
                                    children=[
                                        html.A(
                                            className='header--snap-link',
                                            href='https://snap.uaf.edu',
                                            rel='external',
                                            target='_blank',
                                            children=[
                                                html.Img(src=path_prefix + 'assets/SNAP_acronym_color_square.svg')
                                            ]
                                        )
                                    ]
                                ),
                                html.Div(
                                    className='header--titles',
                                    children=[
                                        html.H1(
                                            'USDA',
                                            className='title is-2'
                                        ),
                                        html.H2(
                                            'Explore local growing conditions under a changing climate.',
                                            className='subtitle is-4'
                                        )
                                    ]
                                )
                            ]
                        )
                    ]
                )
            ]
        )
    ]
)

map_communities_trace = go.Scattermapbox(
    lat=communities['geometry'].y,
    lon=communities['geometry'].x,
    mode='markers',
    marker={
        'size': 15,
        'color': 'rgb(80,80,80)'
    },
    line={
        'color': 'rgb(0, 0, 0)',
        'width': 2
    },
    text=communities.LocationName,
    hoverinfo='text'
)

map_layout = go.Layout(
    autosize=True,
    hovermode='closest',
    mapbox=dict(
        accesstoken=mapbox_access_token,
        zoom=3,
        center=dict(lat=68, lon=-120),
        layers=[
            dict(
                sourcetype='geojson',
                source=json.loads(open('./AK.geo.json', 'r').read()),
                type='fill',
                color='rgba(255,255,255,.1)'
            )
        ]
    ),
    showlegend=False,
    margin=dict(l=0, r=0, t=0, b=0)
)

map_figure = go.Figure({
    'data': [map_communities_trace],
    'layout': map_layout
})

form_elements_section = html.Div(
    className='section',
    children=[
        html.Div(
            className='columns',
            children=[
                html.Div(
                    className='column',
                    children=[
                        html.Button('Update Location', id='location-button', n_clicks=0, className='button is-large'),

                    ]
                )
            ]
        ),
        dcc.Graph(
            id='map',
            figure=map_figure,
            config={
                'displayModeBar': False,
                'scrollZoom': False
            },
            style={'width': '100%', 'height': 600}
        ),
        dcc.RadioItems(
            labelClassName='radio is-radio',
            options=[
                {'label': ' Basic', 'value': 'basic'},
                {'label': ' Light', 'value': 'light'},
                {'label': ' Dark', 'value': 'dark'},
                {'label': ' Satellite', 'value': 'satellite-streets'},
            ],
            id='baselayer',
            value='basic'
        ),
        visdcc.Run_js(id = 'javascript')
    ]
)


footer = html.Footer(
    className='footer has-text-centered',
    children=[
        html.Div(
            children=[
                html.A(
                    href='https://snap.uaf.edu',
                    target='_blank',
                    className='level-item',
                    children=[
                        html.Img(
                            src=path_prefix + 'assets/SNAP.svg'
                        )
                    ]
                ),
                html.A(
                    href='https://uaf.edu/uaf/',
                    target='_blank',
                    className='level-item',
                    children=[
                        html.Img(
                            src=path_prefix + 'assets/UAF.svg'
                        )
                    ]
                )
            ]
        ),
        dcc.Markdown(
            """
            Test tool for USDA
            """,
            className='content is-size-6'
        )
    ]
)

app.layout = html.Div(
    children=[
        header_section,
        html.Div(
            className='section',
            children=[
                html.Div(
                    className='container',
                    children=[
                        html.Div(id='location', className='container', style={ 'visibility': 'hidden' }),
                        form_elements_section,
                        footer
                    ]
                )
            ]
        )
    ]
)

@app.callback(
    Output('javascript', 'run'),
    [Input('location-button', 'n_clicks')])
def myfun(x): 
    if x is None: return ''
    return '''
      getPosition()
      .then((position) => {
          var x = position.coords.latitude + ',' + position.coords.longitude;
          function updateLoc(position){
                setProps({ 
                'event': {
                        'x': position.coords.latitude, 
                        'y': position.coords.longitude
                        }
                });
        }
          $('#location').html(x);
          var target = $('#location-button')[0];
          $('#location-button').off();
          target.addEventListener('click', updateLoc(position));
      });
        '''

@app.callback(
    Output('map', 'figure'),
    [Input('javascript', 'event'), Input('baselayer', 'value')]
)
def update_map(user_loc, baselayer):
    user_trace = {}
    lats = [-65]
    lons = [-147]
    lzoom = 5
    if user_loc is not None:
        lats = [user_loc['x']]
        lons = [user_loc['y']]
        lzoom = 13
        user_trace = go.Scattermapbox(
            lat= lats,
            lon= lons,
            mode='markers',
            marker={
                'size': 20,
                'color': 'rgb(30,70,250)',
                'opacity': 0.7
            },
            text='User',
            hoverinfo='text'
        )
    map_communities_trace = [
        go.Scattermapbox(
            lat=communities['geometry'].y,
            lon=communities['geometry'].x,
            mode='markers',
            marker={
                'size': 12,
                'color': 'rgb(80,80,80)'
            },
            line={
                'color': 'rgb(0, 0, 0)',
                'width': 2
            },
            text=communities.LocationName,
            hoverinfo='text'
        ),
        user_trace
    ]

    map_layout = go.Layout(
        autosize=True,
        hovermode='closest',
        mapbox=dict(
            accesstoken=mapbox_access_token,
            zoom=lzoom,
            center=dict(lat=lats[0], lon=lons[0]),
            layers=[
                dict(
                    sourcetype='geojson',
                    source=json.loads(open('./AK.geo.json', 'r').read()),
                    type='fill',
                    color='rgba(255,255,255,.1)'
                )
            ],
            style=baselayer
        ),
        showlegend=False,
        margin=dict(l=0, r=0, t=0, b=0)
        )

    map_figure = go.Figure({
        'data': map_communities_trace,
        'layout': map_layout
    })

    return map_figure

if __name__ == '__main__':
    application.run(debug=True, port=8080)
