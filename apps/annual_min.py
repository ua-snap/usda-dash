#!/usr/bin/env python3

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
from apps import common
from application import app

path_prefix = os.environ['REQUESTS_PATHNAME_PREFIX']

data_prefix = 'https://s3-us-west-2.amazonaws.com/community-logs-data/'

# AWS Elastic Beanstalk looks for application by default,
# if this variable (application) isn't set you will get a WSGI error.

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
                {'label': ' GFDL', 'value': 'GFDL'},
                {'label': ' NCAR', 'value': 'NCAR'},
            ],
            id='gcm',
            value='GFDL'
        )
    ]
)

config = {
    'toImageButtonOptions': {
        'format': 'svg',
        'height': 600,
        'width': 1600,
        'scale': 1
    }
}

graph_layout = html.Div(
    className='container',
    children=[
        dcc.Graph(id='acharts', config=config)
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
                    ]
                ),
                gcm_layout
            ]
        )
    ]
)


layout = html.Div(
    children=[
        common.header(),
        html.Div(
            className='section',
            children=[
                html.Div(
                    className='container',
                    children=[
                        html.Div(id='location', className='container', style={ 'visibility': 'hidden' }),
                        form_elements_section,
                        common.footer()
                    ]
                )
            ]
        )
    ]
)

def add_traces(community, gcm, figure):
    community_name = re.sub('[^A-Za-z0-9]+', '', community) + '_' + gcm
    comm_filename = community_name

    df = pd.read_csv('https://s3-us-west-2.amazonaws.com/community-logs-data/' + comm_filename + '.csv')
    imperial_conversion_lu = {'temp':1.8,'precip':0.0393701}
    df['temp'] = df['temp'] * imperial_conversion_lu['temp'] + 32
    df['time'] = pd.to_datetime(df['time'], format='%Y-%m-%d')
    years = {}
    if (gcm == 'ERA'):
        for i in range (1980,2010,30):
            years[i] = { 'date': {}, 'minmin': [], 'maxmin': [] }
    else:
        for i in range (2010,2100,30):
            years[i] = { 'date': {}, 'minmin': [], 'maxmin': [] }
    decade_lu = { '1980': '#999999', '2010': '#bdd7e7' , '2040': '#6baed6', '2070': '#2171b5'}
    for key in sorted(years):
        df_t = df[df['time'].dt.year >= int(key)]
        df_annual = df_t[df_t['time'].dt.year < int(key) + 30]
        if (gcm == 'ERA'):
            title = str(key) + 's (Hist)'
        else: 
            title = str(key) + 's (Projected)'
        dx = df_annual.set_index('time')
        dxx = dx.to_xarray()
        month_day_str = xr.DataArray(dxx.indexes['time'].strftime('%m-%d'), coords=dxx.coords, name='month_day_str')
        ds_min = dxx.groupby(month_day_str).min()
        figure['data'].append({
            'x': month_day_str.values,
            'y': ds_min['temp'].values,
            'hoverinfo': 'y',
            'name': title,
            'text': ds_min['temp'].values,
            'mode': 'markers',
            'marker': {
                'color': decade_lu[str(key)]
            }
        })


@app.callback(
    Output('acharts', 'figure'),
    inputs=[
        Input('community', 'value'),
        Input('gcm', 'value')
    ]
)
def temp_chart(community, gcm):
    figure = {}
    figure['data'] = []
    add_traces(community, 'ERA', figure)
    add_traces(community, gcm, figure)

    layout = {
            'title': 'Daily Minimum Temps (' + unit_lu['temp']['imperial'] + '): ' + community + ', Alaska, ' + gcm + ' model',
	'hovermode': 'closest',
        'hoverlabel': {
            'namelength': 20
        },
        'legend': {
            'text': 'Legend Title',
            'traceorder': 'reversed'
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
    figure['layout'] = layout
    return figure
