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
                {'label': ' Model Projection (GFDL)', 'value': 'GFDL'},
                {'label': ' Model Projection (NCAR)', 'value': 'NCAR'},
            ],
            id='gcm',
            value='GFDL'
        )
    ]
)

threshold_layout = dcc.Dropdown(
    id='threshold',
    options=[
        {'label': ' 28 °F (Hard Frost)', 'value': 28},
        {'label': ' 32 °F (Light Frost)', 'value': 32},
        {'label': ' 40 °F (Cold Crops)', 'value': 40},
        {'label': ' 50 °F (Warm Crops)', 'value': 50},
    ],
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

def add_traces(community, threshold, gcm, figure, bx):
    community_name = re.sub('[^A-Za-z0-9]+', '', community) + '_' + gcm
    comm_filename = community_name

    df = pd.read_csv('https://s3-us-west-2.amazonaws.com/community-logs-data/' + comm_filename + '.csv', index_col = 'time')
    imperial_conversion_lu = {'temp':1.8,'precip':0.0393701}
    df[community_name] = df[community_name] * imperial_conversion_lu['temp'] + 32
    if (gcm == 'ERA'):
        minyear = 1980
        maxyear = 2010
    else:
        minyear = 2010
        maxyear = 2101
    dx = df.to_xarray()
    dx.rename({community_name: 'temp'},inplace=True)
    dx['time'] = pd.to_datetime(dx['time'], format='%Y-%m-%d')
    for i in range(minyear,maxyear-9,10):
        dx_decade = dx.temp[dx['time'].dt.year >= i]
        dx_decade = dx_decade[dx_decade['time'].dt.year < i+10]
        month_day_str = xr.DataArray(dx_decade.indexes['time'].strftime('%m-%d'), coords=dx_decade.coords, name='month_day_str')
        #dx_mean = dx_decade.groupby(month_day_str).mean()
        if (gcm != 'ERA'):
            dx_pre_mean = dx_decade.groupby(month_day_str).mean()
            dx_mean = dx_pre_mean - (bx * 1.8)
        else:
            dx_mean = dx_decade.groupby(month_day_str).mean()
        df_pre = dx_mean[dx_mean.values > threshold]
        df_pre_thresh = df_pre - threshold
        df_cumsum = df_pre_thresh.cumsum()
        if (gcm == 'ERA'):
            linecolor = '#2d2d2d'
        else:
            yearr = 230 - (i - minyear) / (maxyear - minyear) * 210 
            yearg = 250 - (i - minyear) / (maxyear - minyear) * 130
            yearb = 250 - (i - minyear) / (maxyear - minyear) * 210 
            linecolor = 'rgb(' + str(yearr) + ',' + str(yearg) + ',' + str(yearb) + ')'
        figure['data'].append({
            'x': df_cumsum['month_day_str'].values,
            'y': df_cumsum.values,
            'hoverinfo': 'text+y',
            'name': str(i) + '-' + str(i+9),
            'text': str(i) + '-' + str(i+9),

            'mode': 'lines',
            'marker': {
                'color': linecolor
            }
        })

@app.callback(
    Output('ccharts', 'figure'),
    inputs=[
        Input('community', 'value'),
        Input('threshold', 'value'),
        Input('gcm', 'value')
    ]
)
def temp_chart(community, threshold, gcm):
    figure = {}
    figure['data'] = []
    bx = common.calc_bias(community, gcm)
    add_traces(community, threshold, 'ERA', figure, bx)
    add_traces(community, threshold, gcm, figure, bx)
    layout = {
            'title': 'Cumulative Growing Degrees over ' + str(threshold) + unit_lu['temp']['imperial'] + ': ' + community + ', Alaska' +  ', ' + gcm + ' model',
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
            'categoryarray': ['01-01', '01-02', '01-03', '01-04', '01-05', '01-06', '01-07', '01-08', '01-09', '01-10', '01-11', '01-12', '01-13', '01-14', '01-15', '01-16', '01-17', '01-18', '01-19', '01-20', '01-21', '01-22', '01-23', '01-24', '01-25', '01-26', '01-27', '01-28', '01-29', '01-30', '01-31', '02-01', '02-02', '02-03', '02-04', '02-05', '02-06', '02-07', '02-08', '02-09', '02-10', '02-11', '02-12', '02-13', '02-14', '02-15', '02-16', '02-17', '02-18', '02-19', '02-20', '02-21', '02-22', '02-23', '02-24', '02-25', '02-26', '02-27', '02-28', '02-29', '03-01', '03-02', '03-03', '03-04', '03-05', '03-06', '03-07', '03-08', '03-09', '03-10', '03-11', '03-12', '03-13', '03-14', '03-15', '03-16', '03-17', '03-18', '03-19', '03-20', '03-21', '03-22', '03-23', '03-24', '03-25', '03-26', '03-27', '03-28', '03-29', '03-30', '03-31', '04-01', '04-02', '04-03', '04-04', '04-05', '04-06', '04-07', '04-08', '04-09', '04-10', '04-11', '04-12', '04-13', '04-14', '04-15', '04-16', '04-17', '04-18', '04-19', '04-20', '04-21', '04-22', '04-23', '04-24', '04-25', '04-26', '04-27', '04-28', '04-29', '04-30', '05-01', '05-02', '05-03', '05-04', '05-05', '05-06', '05-07', '05-08', '05-09', '05-10', '05-11', '05-12', '05-13', '05-14', '05-15', '05-16', '05-17', '05-18', '05-19', '05-20', '05-21', '05-22', '05-23', '05-24', '05-25', '05-26', '05-27', '05-28', '05-29', '05-30', '05-31', '06-01', '06-02', '06-03', '06-04', '06-05', '06-06', '06-07', '06-08', '06-09', '06-10', '06-11', '06-12', '06-13', '06-14', '06-15', '06-16', '06-17', '06-18', '06-19', '06-20', '06-21', '06-22', '06-23', '06-24', '06-25', '06-26', '06-27', '06-28', '06-29', '06-30', '07-01', '07-02', '07-03', '07-04', '07-05', '07-06', '07-07', '07-08', '07-09', '07-10', '07-11', '07-12', '07-13', '07-14', '07-15', '07-16', '07-17', '07-18', '07-19', '07-20', '07-21', '07-22', '07-23', '07-24', '07-25', '07-26', '07-27', '07-28', '07-29', '07-30', '07-31', '08-01', '08-02', '08-03', '08-04', '08-05', '08-06', '08-07', '08-08', '08-09', '08-10', '08-11', '08-12', '08-13', '08-14', '08-15', '08-16', '08-17', '08-18', '08-19', '08-20', '08-21', '08-22', '08-23', '08-24', '08-25', '08-26', '08-27', '08-28', '08-29', '08-30', '08-31', '09-01', '09-02', '09-03', '09-04', '09-05', '09-06', '09-07', '09-08', '09-09', '09-10', '09-11', '09-12', '09-13', '09-14', '09-15', '09-16', '09-17', '09-18', '09-19', '09-20', '09-21', '09-22', '09-23', '09-24', '09-25', '09-26', '09-27', '09-28', '09-29', '09-30', '10-01', '10-02', '10-03', '10-04', '10-05', '10-06', '10-07', '10-08', '10-09', '10-10', '10-11', '10-12', '10-13', '10-14', '10-15', '10-16', '10-17', '10-18', '10-19', '10-20', '10-21', '10-22', '10-23', '10-24', '10-25', '10-26', '10-27', '10-28', '10-29', '10-30', '10-31', '11-01', '11-02', '11-03', '11-04', '11-05', '11-06', '11-07', '11-08', '11-09', '11-10', '11-11', '11-12', '11-13', '11-14', '11-15', '11-16', '11-17', '11-18', '11-19', '11-20', '11-21', '11-22', '11-23', '11-24', '11-25', '11-26', '11-27', '11-28', '11-29', '11-30', '12-01', '12-02', '12-03', '12-04', '12-05', '12-06', '12-07', '12-08', '12-09', '12-10', '12-11', '12-12', '12-13', '12-14', '12-15', '12-16', '12-17', '12-18', '12-19', '12-20', '12-21', '12-22', '12-23', '12-24', '12-25', '12-26', '12-27', '12-28', '12-29', '12-30', '12-31']
            #'categoryarray': [ 'January 01', 'January 02', 'January 03', 'January 04', 'January 05', 'January 06', 'January 07', 'January 08', 'January 09', 'January 10', 'January 11', 'January 12', 'January 13', 'January 14', 'January 15', 'January 16', 'January 17', 'January 18', 'January 19', 'January 20', 'January 21', 'January 22', 'January 23', 'January 24', 'January 25', 'January 26', 'January 27', 'January 28', 'January 29', 'January 30', 'January 31', 'February 01', 'February 02', 'February 03', 'February 04', 'February 05', 'February 06', 'February 07', 'February 08', 'February 09', 'February 10', 'February 11', 'February 12', 'February 13', 'February 14', 'February 15', 'February 16', 'February 17', 'February 18', 'February 19', 'February 20', 'February 21', 'February 22', 'February 23', 'February 24', 'February 25', 'February 26', 'February 27', 'February 28', 'February 29', 'March 01', 'March 02', 'March 03', 'March 04', 'March 05', 'March 06', 'March 07', 'March 08', 'March 09', 'March 10', 'March 11', 'March 12', 'March 13', 'March 14', 'March 15', 'March 16', 'March 17', 'March 18', 'March 19', 'March 20', 'March 21', 'March 22', 'March 23', 'March 24', 'March 25', 'March 26', 'March 27', 'March 28', 'March 29', 'March 30', 'March 31', 'April 01', 'April 02', 'April 03', 'April 04', 'April 05', 'April 06', 'April 07', 'April 08', 'April 09', 'April 10', 'April 11', 'April 12', 'April 13', 'April 14', 'April 15', 'April 16', 'April 17', 'April 18', 'April 19', 'April 20', 'April 21', 'April 22', 'April 23', 'April 24', 'April 25', 'April 26', 'April 27', 'April 28', 'April 29', 'April 30', 'May 01', 'May 02', 'May 03', 'May 04', 'May 05', 'May 06', 'May 07', 'May 08', 'May 09', 'May 10', 'May 11', 'May 12', 'May 13', 'May 14', 'May 15', 'May 16', 'May 17', 'May 18', 'May 19', 'May 20', 'May 21', 'May 22', 'May 23', 'May 24', 'May 25', 'May 26', 'May 27', 'May 28', 'May 29', 'May 30', 'May 31', 'June 01', 'June 02', 'June 03', 'June 04', 'June 05', 'June 06', 'June 07', 'June 08', 'June 09', 'June 10', 'June 11', 'June 12', 'June 13', 'June 14', 'June 15', 'June 16', 'June 17', 'June 18', 'June 19', 'June 20', 'June 21', 'June 22', 'June 23', 'June 24', 'June 25', 'June 26', 'June 27', 'June 28', 'June 29', 'June 30', 'July 01', 'July 02', 'July 03', 'July 04', 'July 05', 'July 06', 'July 07', 'July 08', 'July 09', 'July 10', 'July 11', 'July 12', 'July 13', 'July 14', 'July 15', 'July 16', 'July 17', 'July 18', 'July 19', 'July 20', 'July 21', 'July 22', 'July 23', 'July 24', 'July 25', 'July 26', 'July 27', 'July 28', 'July 29', 'July 30', 'July 31', 'August 01', 'August 02', 'August 03', 'August 04', 'August 05', 'August 06', 'August 07', 'August 08', 'August 09', 'August 10', 'August 11', 'August 12', 'August 13', 'August 14', 'August 15', 'August 16', 'August 17', 'August 18', 'August 19', 'August 20', 'August 21', 'August 22', 'August 23', 'August 24', 'August 25', 'August 26', 'August 27', 'August 28', 'August 29', 'August 30', 'August 31', 'September 01', 'September 02', 'September 03', 'September 04', 'September 05', 'September 06', 'September 07', 'September 08', 'September 09', 'September 10', 'September 11', 'September 12', 'September 13', 'September 14', 'September 15', 'September 16', 'September 17', 'September 18', 'September 19', 'September 20', 'September 21', 'September 22', 'September 23', 'September 24', 'September 25', 'September 26', 'September 27', 'September 28', 'September 29', 'September 30', 'October 01', 'October 02', 'October 03', 'October 04', 'October 05', 'October 06', 'October 07', 'October 08', 'October 09', 'October 10', 'October 11', 'October 12', 'October 13', 'October 14', 'October 15', 'October 16', 'October 17', 'October 18', 'October 19', 'October 20', 'October 21', 'October 22', 'October 23', 'October 24', 'October 25', 'October 26', 'October 27', 'October 28', 'October 29', 'October 30', 'October 31', 'November 01', 'November 02', 'November 03', 'November 04', 'November 05', 'November 06', 'November 07', 'November 08', 'November 09', 'November 10', 'November 11', 'November 12', 'November 13', 'November 14', 'November 15', 'November 16', 'November 17', 'November 18', 'November 19', 'November 20', 'November 21', 'November 22', 'November 23', 'November 24', 'November 25', 'November 26', 'November 27', 'November 28', 'November 29', 'November 30', 'December 01', 'December 02', 'December 03', 'December 04', 'December 05', 'December 06', 'December 07', 'December 08', 'December 09', 'December 10', 'December 11', 'December 12', 'December 13', 'December 14', 'December 15', 'December 16', 'December 17', 'December 18', 'December 19', 'December 20', 'December 21', 'December 22', 'December 23', 'December 24', 'December 25', 'December 26', 'December 27', 'December 28', 'December 29', 'December 30', 'December 31' ]
        }
    }
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
