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

#app.title = 'SNAP - USDA Garden Helper'

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
for i in reversed(range(0,15,5)):
    thresholds.append(i)

threshold_layout = dcc.Dropdown(
    id='threshold',
    options=[{'label':str(t) + unit_lu['temp']['imperial'], 'value':t} for t in thresholds],
    value=32
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
        dcc.Graph(id='ccharts', config=config)
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



@app.callback(
    Output('ccharts', 'figure'),
    inputs=[
        Input('community', 'value'),
        Input('threshold', 'value'),
        Input('gcm', 'value')
    ]
)
def temp_chart(community, threshold, gcm):
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
    figure = {}
    figure['data'] = []
    #for i in range(1980,2101):
    for i in range(1990,1992):
        df_annual = df[df['time'].dt.year == i]
        df_pre = df_annual[df_annual[community_name] > threshold]
        print(df_annual)
        df_pre = df_pre[community_name] - threshold
        print(df_pre)
        df_cumsum = df_pre.cumsum()

        dx = df_annual.set_index('time')
        dxx = dx.to_xarray()
        month_day_str = xr.DataArray(dxx.indexes['time'].strftime('%m-%d'), coords=dxx.coords, name='month_day_str')

        print(df_cumsum)
        figure['data'].append({
            'x': month_day_str.values,
            'y': df_cumsum.values,
            'hoverinfo': 'text+y',
            'name': i,
            'text': i,
            'mode': 'lines',
            'marker': {
            }
        })
    '''
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
            'mode': 'lines',
            'marker': {
                'color': decade_lu[str(key)]
            }
        })
    '''
    figure['layout'] = layout
    return figure
