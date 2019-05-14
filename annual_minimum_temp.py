'''
Template for SNAP Dash apps.
'''
import os
import json
import plotly.graph_objs as go
import xarray as xr
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_dangerously_set_inner_html as ddsih
import pandas as pd
import geopandas as gpd
import numpy as np
import urllib, json
import re
from dash.dependencies import Input, Output, State

path_prefix = os.environ['REQUESTS_PATHNAME_PREFIX']

data_prefix = 'https://s3-us-west-2.amazonaws.com/community-logs-data/'

def get_max_days(datayear, community, threshold):
    day_counter = 0
    minmin = 100
    maxmin = 100
    max_days = 0
    startdate = ''
    enddate = ''
    max_start = ''
    max_end = ''
    for i, (index,row) in enumerate(datayear.iterrows()):
        if (row[community] > threshold):
            if (day_counter == 0):
                startdate = row['time']
            day_counter = day_counter + 1
        else:
            enddate = row['time']
            if (day_counter > max_days):
                max_days = day_counter
                max_start = startdate
                max_end = enddate
            day_counter = 0
            startdate = ''
            enddate = ''
        if i == len(datayear) - 1:
            if (day_counter > max_days):
                max_days = day_counter
                max_start = startdate
                max_end = row['time']
    return { 'ndays': max_days, 'startdate': max_start, 'enddate': max_end }


external_scripts = ['https://code.jquery.com/jquery-3.3.1.min.js']

app = dash.Dash(external_scripts = external_scripts)
app.config.requests_pathname_prefix = os.environ['REQUESTS_PATHNAME_PREFIX']

# AWS Elastic Beanstalk looks for application by default,
# if this variable (application) isn't set you will get a WSGI error.
application = app.server

app.title = 'SNAP - USDA Garden Helper'

#mapbox_access_token = os.environ['MAPBOX_ACCESS_TOKEN']
path_prefix = os.environ['REQUESTS_PATHNAME_PREFIX']
communities = gpd.read_file('CommunityList.json')
names = list(communities.LocationName)

community_layout = dcc.Dropdown(
    id='community',
    options=[{'label':name, 'value':name} for name in names],
    value='Fairbanks'
)

unit_lu = {
    'temp': {
        'imperial': ' °F',
        'metric': ' °C'
    },
    'precip': {
        'imperial': 'in',
        'metric': 'mm'
    }
}

gcm_layout = html.Div(
    className='control',
    children=[
        html.Label('Select Dataset', className='label'),
        dcc.RadioItems(
            labelClassName='radio',
            options=[
                {'label': ' ERA', 'value': 'ERA'},
                {'label': ' GFDL', 'value': 'GFDL'},
                {'label': ' NCAR', 'value': 'NCAR'},
            ],
            id='gcm',
            value='ERA'
        )
    ]
)

thresholds = []
for i in reversed(range(-50,100)):
    thresholds.append(i)

threshold_layout = dcc.Dropdown(
    id='threshold',
    options=[{'label':str(t) + unit_lu['temp']['imperial'], 'value':t} for t in thresholds],
    value=32
)

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

#map_communities_trace = go.Scattermapbox(
#    lat=communities['geometry'].y,
#    lon=communities['geometry'].x,
#    mode='markers',
#    marker={
#        'size': 15,
#        'color': 'rgb(80,80,80)'
#    },
#    line={
#        'color': 'rgb(0, 0, 0)',
#        'width': 2
#    },
#    text=communities.LocationName,
#    hoverinfo='text'
#)

#map_layout = go.Layout(
#    autosize=True,
#    hovermode='closest',
#    mapbox=dict(
#        accesstoken=mapbox_access_token,
#        zoom=3,
#        center=dict(lat=68, lon=-120),
#        #layers=[
#            #dict(
#                #sourcetype='geojson',
#                #source=json.loads(open('./AK.geo.json', 'r').read()),
#                #type='fill',
#                #color='rgba(255,255,255,.1)'
#            #)
#        #]
#    ),
#    showlegend=False,
#    margin=dict(l=0, r=0, t=0, b=0)
#)

#map_figure = go.Figure({
#    'data': [map_communities_trace],
#    'layout': map_layout
#})

config = {
    'toImageButtonOptions': {
        'title': 'Export to SVG',
        'format': 'svg',
        'height': 600,
        'width': 1600,
        'scale': 1
    }
}

graph_layout = html.Div(
    className='container',
    children=[
        dcc.Graph(id='tcharts', config=config)
    ]
)

form_elements_section = html.Div(
    className='section',
    children=[
        graph_layout,
        html.Div(
            className='container',
            children=[
                html.Div(
                    className='columns',
                    children=[
                        html.Div(
                            className='column',
                            children=[  
                                html.Label('Select Community', className='label'),
                                community_layout 
                            ]
                        ),
                        html.Div(
                            className='column',
                            children=[ 
                                html.Label('Select Minimum Temperature Threshold', className='label'),
                                threshold_layout 
                            ]
                        )
                    ]
                ),
                gcm_layout
            ]
        )
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
    Output('tcharts', 'figure'),
    inputs=[
        Input('community', 'value'),
        Input('threshold', 'value'),
        Input('gcm', 'value')
    ]
)
def temp_chart(community, threshold, gcm):
    station = 'PAFA'
    acis_data = {}

    community_name = re.sub('[^A-Za-z0-9]+', '', community) + '_' + gcm
    comm_filename = community_name

    df = pd.read_csv('https://s3-us-west-2.amazonaws.com/community-logs-data/' + comm_filename + '.csv')
    imperial_conversion_lu = {'temp':1.8,'precip':0.0393701}
    df[community_name] = df[community_name] * imperial_conversion_lu['temp'] + 32
    df['time'] = pd.to_datetime(df['time'], format='%Y-%m-%d')
    layout = {
        'title': community + ', Alaska: Daily Minimum Temps ' + unit_lu['temp']['imperial'] + ', ' + gcm + ' model',
	'hovermode': 'closest',
        'hoverlabel': {
            'namelength': 20
        },
        'legend': {
            'text': 'Legend Title'
        },
	'type': 'date',
	'height': 500,
	'yaxis': {
	    'tickformat': 'd',
            'hoverformat': '.2f'
	},
        'xaxis': { 
            'type': 'category',
        }
    }
    years = {}
    for i in range (1980,2100,30):
        years[i] = { 'date': {}, 'minmin': [], 'maxmin': [] }
    figure = {}
    figure['data'] = []
    decade_lu = { '1980': 'rgb(150,150,150)', '2010':'rgb(0,50,150)' , '2040': 'rgb(75,125,255)', '2070': 'rgb(175,225,255)'}
    for key in sorted(years):
        df_t = df[df['time'].dt.year >= int(key)]
        df_annual = df_t[df_t['time'].dt.year < int(key) + 30]

        dx = df_annual.set_index('time')
        dxx = dx.to_xarray()
        month_day_str = xr.DataArray(dxx.indexes['time'].strftime('%m-%d'), coords=dxx.coords, name='month_day_str')
        ds_min = dxx.groupby(month_day_str).min()
        figure['data'].append({
            'x': month_day_str.values,
            'y': ds_min[community_name].values,
            'hoverinfo': 'y',
            'name': str(key) + 's',
            'text': ds_min[community_name].values,
            'mode': 'markers',
            'marker': {
                'color': decade_lu[str(key)]
            }
        })
        '''
        figure['data'].append({
            'x': categoryarray,
            'y': ds_max[community_name].values,
            'name': str(key) + 's max',
            'mode': 'markers',
            'marker': {
                'color': decade_lu[str(key)]
            }
        })
        figure['data'].append({
            'x': categoryarray,
            'y': ds_mean[community_name].values,
            'name': str(key) + 's mean',
            'mode': 'markers',
            'marker': {
                'color': decade_lu[str(key)]
            }
        })
        '''
    figure['layout'] = layout
    return figure
    

if __name__ == '__main__':
    application.run(debug=True, port=8180)
