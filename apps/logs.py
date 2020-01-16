#!/usr/bin/env python3
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
import dash_table
import pandas as pd
import xarray as xr
import geopandas as gpd
import numpy as np
import urllib, json
import re
from dash.dependencies import Input, Output, State
from apps import common
from application import app

path_prefix = os.environ['REQUESTS_PATHNAME_PREFIX']

data_prefix = 'https://s3-us-west-2.amazonaws.com/community-logs-data/'

season_table_data = gpd.read_file('season.csv')

def get_max_days_alt(datayear, community, threshold, gcm):
    df_bools = datayear['temp'] > threshold
    max_days = 0
    boolvals = (~df_bools).cumsum()[df_bools]
    logs = boolvals.value_counts()
    max_days = logs.max()
    check_eq = boolvals[boolvals == logs.index[0]]
    clipbools = check_eq.clip(logs.index[0],logs.index[0])

    startdateid = check_eq.index[0]
    startdate = datayear.loc[startdateid].time.strftime('%m-%d')
    enddate = (datayear.loc[startdateid].time + pd.DateOffset(days=int(logs.iloc[0]))).strftime('%m-%d')


    return { 'ndays': max_days, 'startdate': startdate, 'enddate': enddate }

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
        'imperial': '°F',
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
        html.Label('Choose Dataset', className='label'),
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
        {'label': ' 28°F (Hard Frost)', 'value': 28},
        {'label': ' 32°F (Light Frost)', 'value': 32},
        {'label': ' 40°F (Cold Crops)', 'value': 40},
        {'label': ' 50°F (Warm Crops)', 'value': 50},
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
        dcc.Graph(id='tcharts', config=config)
    ]
)

table_columns = [
  {"name": "Baseline Temperature Threshold (°F)", "id": "baselinetemp"},
  {"name": "Species or Variety", "id": "species"},
  {"name": "Minimum number of days to maturity", "id": "mindaysmaturity"},
]

# Initial data table setup
initial = season_table_data
data_table = dash_table.DataTable(
    id="season-table",
    columns=table_columns,
    style_cell={"whiteSpace": "normal", "textAlign": "left"},
    data=list(initial.to_dict("index").values()),
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
                                html.Label('Choose Community', className='label'),
                                community_layout 
                            ]
                        ),
                        html.Div(
                            className='column',
                            children=[ 
                                html.Label('Choose Minimum Temperature Threshold', className='label'),
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
        html.Div(
            className='section',
            children=[
                html.Div(
                    className='container',
                    children=[
                        html.Div(id='location', className='container', style={ 'visibility': 'hidden' }),
                        form_elements_section,
                        data_table,
                        html.Br(),
                        html.Br(),
                        dcc.Markdown(
                            """
### Length of Growing Season
##### About growing season length
Time between the last cold day in spring (based on the temperature threshold you select: 32°F, 40°F, or 50°F) and the first cold day in fall. Here, you can see projections of start/end dates and the number of days in between. This can help you decide if a crop is worth planting in your area. ”Days to maturity” information is often provided on seed packets. But keep in mind that cool temperatures can slow growth, so also check our “Growing Degree Days” tool.
##### How to choose a temperature threshold
Planting guides refer to “last frost” in spring and “first frost” in fall, implying minimum daily temperatures of 32°F. We offer more thresholds to provide flexibility in considering cold-hardy crops that may be harvested only when a hard frost is reached (28°F), or more delicate crops that cannot grow when temperatures are below a higher threshold. Such plants might be kept in a greenhouse until a later planting date, and harvested earlier. Learn more about specific crops here link
##### Why does the growing season seem so irregular?
If you choose a high temperature threshold, or live in a very cold region, you may see results that look short and uneven. This is because the tool finds the longest consecutive period during which the daily minimum temperature never drops below the selected temperature. If just one day is below that value, the “season” ends at that point. Be sure to choose thresholds that make sense for your area.
                            """
                        ,
                        className='content is-size-6'
                        ),
			common.infotext(),
                    ]
                )
            ]
        )
    ]
)

def add_time_series(community,threshold,gcm,figure):
    community_name = re.sub('[^A-Za-z0-9]+', '', community) + '_' + gcm
    comm_filename = community_name
    df = pd.read_csv('https://s3-us-west-2.amazonaws.com/community-logs-data/min/' + comm_filename + '_min.csv')
    imperial_conversion_lu = {'temp':1.8,'precip':0.0393701}
    df['temp'] = df['temp'] * imperial_conversion_lu['temp'] + 32
    df['time'] = pd.to_datetime(df['time'])
    years = {}
    #for i in range (1971,2100):
    minyear = 1980
    maxyear = 2101
    if (gcm == 'ERA'):
        minyear = 1980
        maxyear = 2010
    else:
        minyear = 2010
        maxyear = 2100
    for i in range (minyear,maxyear,1):
        years[i] = {}

    for key in sorted(years):
        df_annual = df[df['time'].dt.year == int(key)]
        years[key] = get_max_days_alt(df_annual, community_name, threshold, gcm)
    for i in range(minyear,maxyear-9,10):
        decade_dict = {}
        for j in range(0,10):
            decade_dict[i + j] =  years[i + j]
        dsorted = sorted(decade_dict, key=lambda key: decade_dict[key]['ndays'])
        decade_90pct = years[dsorted[1]]
        dates = [decade_90pct['startdate'], decade_90pct['enddate']]
        yrs = [str(i) + '-' +  str(i + 9), str(i) + '-' +  str(i + 9)]
        dash = ''
        if (gcm == 'ERA'):
            color = '#999999'
            name = str(decade_90pct['ndays']) + ' Days > ' + str(threshold) + unit_lu['temp']['imperial'] + ' '
            dash = ''
        else: 
            color = '#008000'
            name = str(decade_90pct['ndays']) + ' Days > ' + str(threshold) + unit_lu['temp']['imperial'] + ' '
            dash = 'dash'

        figure['data'].append({
            'x': dates,
            'y': yrs,
            #'text': ['Date of Thaw','Date of Freeze'],
            'name': name,
            'line': {
                'width': 5,
                'color': color
            },
            'marker': {
                'size': 15,
                'line': {
                    'width': 5
                }
            }
        })

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
    #with urllib.request.urlopen('http://data.rcc-acis.org/StnData?sid=' + station + '&sdate=1950-01-01&edate=2019-03-15&elems=4') as url:
    #    acis_data = json.loads(url.read().decode())
    figure = {}
    figure['data'] = []
    add_time_series(community, threshold, 'ERA', figure)
    add_time_series(community, threshold, gcm, figure)
    layout = {
        'title': 'Growing Season (Start, Length, End)<br>Number of Days > ' + str(threshold) + unit_lu['temp']['imperial'] + '<br>' + community + ', Alaska, Historical and Projected [' + gcm + '] model',
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
            'autorange': 'reversed',
	    'tickformat': 'd',
            'title': {
                'text': 'Decades'
            },
	},
        'xaxis': { 
            'range': ['Jan 01', 'Dec 31'],
            'type': 'category',
	    'tickformat': '%m/%d',
            'categoryarray': ['01-01', '01-02', '01-03', '01-04', '01-05', '01-06', '01-07', '01-08', '01-09', '01-10', '01-11', '01-12', '01-13', '01-14', '01-15', '01-16', '01-17', '01-18', '01-19', '01-20', '01-21', '01-22', '01-23', '01-24', '01-25', '01-26', '01-27', '01-28', '01-29', '01-30', '01-31', '02-01', '02-02', '02-03', '02-04', '02-05', '02-06', '02-07', '02-08', '02-09', '02-10', '02-11', '02-12', '02-13', '02-14', '02-15', '02-16', '02-17', '02-18', '02-19', '02-20', '02-21', '02-22', '02-23', '02-24', '02-25', '02-26', '02-27', '02-28', '02-29', '03-01', '03-02', '03-03', '03-04', '03-05', '03-06', '03-07', '03-08', '03-09', '03-10', '03-11', '03-12', '03-13', '03-14', '03-15', '03-16', '03-17', '03-18', '03-19', '03-20', '03-21', '03-22', '03-23', '03-24', '03-25', '03-26', '03-27', '03-28', '03-29', '03-30', '03-31', '04-01', '04-02', '04-03', '04-04', '04-05', '04-06', '04-07', '04-08', '04-09', '04-10', '04-11', '04-12', '04-13', '04-14', '04-15', '04-16', '04-17', '04-18', '04-19', '04-20', '04-21', '04-22', '04-23', '04-24', '04-25', '04-26', '04-27', '04-28', '04-29', '04-30', '05-01', '05-02', '05-03', '05-04', '05-05', '05-06', '05-07', '05-08', '05-09', '05-10', '05-11', '05-12', '05-13', '05-14', '05-15', '05-16', '05-17', '05-18', '05-19', '05-20', '05-21', '05-22', '05-23', '05-24', '05-25', '05-26', '05-27', '05-28', '05-29', '05-30', '05-31', '06-01', '06-02', '06-03', '06-04', '06-05', '06-06', '06-07', '06-08', '06-09', '06-10', '06-11', '06-12', '06-13', '06-14', '06-15', '06-16', '06-17', '06-18', '06-19', '06-20', '06-21', '06-22', '06-23', '06-24', '06-25', '06-26', '06-27', '06-28', '06-29', '06-30', '07-01', '07-02', '07-03', '07-04', '07-05', '07-06', '07-07', '07-08', '07-09', '07-10', '07-11', '07-12', '07-13', '07-14', '07-15', '07-16', '07-17', '07-18', '07-19', '07-20', '07-21', '07-22', '07-23', '07-24', '07-25', '07-26', '07-27', '07-28', '07-29', '07-30', '07-31', '08-01', '08-02', '08-03', '08-04', '08-05', '08-06', '08-07', '08-08', '08-09', '08-10', '08-11', '08-12', '08-13', '08-14', '08-15', '08-16', '08-17', '08-18', '08-19', '08-20', '08-21', '08-22', '08-23', '08-24', '08-25', '08-26', '08-27', '08-28', '08-29', '08-30', '08-31', '09-01', '09-02', '09-03', '09-04', '09-05', '09-06', '09-07', '09-08', '09-09', '09-10', '09-11', '09-12', '09-13', '09-14', '09-15', '09-16', '09-17', '09-18', '09-19', '09-20', '09-21', '09-22', '09-23', '09-24', '09-25', '09-26', '09-27', '09-28', '09-29', '09-30', '10-01', '10-02', '10-03', '10-04', '10-05', '10-06', '10-07', '10-08', '10-09', '10-10', '10-11', '10-12', '10-13', '10-14', '10-15', '10-16', '10-17', '10-18', '10-19', '10-20', '10-21', '10-22', '10-23', '10-24', '10-25', '10-26', '10-27', '10-28', '10-29', '10-30', '10-31', '11-01', '11-02', '11-03', '11-04', '11-05', '11-06', '11-07', '11-08', '11-09', '11-10', '11-11', '11-12', '11-13', '11-14', '11-15', '11-16', '11-17', '11-18', '11-19', '11-20', '11-21', '11-22', '11-23', '11-24', '11-25', '11-26', '11-27', '11-28', '11-29', '11-30', '12-01', '12-02', '12-03', '12-04', '12-05', '12-06', '12-07', '12-08', '12-09', '12-10', '12-11', '12-12', '12-13', '12-14', '12-15', '12-16', '12-17', '12-18', '12-19', '12-20', '12-21', '12-22', '12-23', '12-24', '12-25', '12-26', '12-27', '12-28', '12-29', '12-30', '12-31']
	    #'categoryarray': [ 'Jan 01', 'Jan 02', 'Jan 03', 'Jan 04', 'Jan 05', 'Jan 06', 'Jan 07', 'Jan 08', 'Jan 09', 'Jan 10', 'Jan 11', 'Jan 12', 'Jan 13', 'Jan 14', 'Jan 15', 'Jan 16', 'Jan 17', 'Jan 18', 'Jan 19', 'Jan 20', 'Jan 21', 'Jan 22', 'Jan 23', 'Jan 24', 'Jan 25', 'Jan 26', 'Jan 27', 'Jan 28', 'Jan 29', 'Jan 30', 'Jan 31', 'Feb 01', 'Feb 02', 'Feb 03', 'Feb 04', 'Feb 05', 'Feb 06', 'Feb 07', 'Feb 08', 'Feb 09', 'Feb 10', 'Feb 11', 'Feb 12', 'Feb 13', 'Feb 14', 'Feb 15', 'Feb 16', 'Feb 17', 'Feb 18', 'Feb 19', 'Feb 20', 'Feb 21', 'Feb 22', 'Feb 23', 'Feb 24', 'Feb 25', 'Feb 26', 'Feb 27', 'Feb 28', 'Feb 29', 'Mar 01', 'Mar 02', 'Mar 03', 'Mar 04', 'Mar 05', 'Mar 06', 'Mar 07', 'Mar 08', 'Mar 09', 'Mar 10', 'Mar 11', 'Mar 12', 'Mar 13', 'Mar 14', 'Mar 15', 'Mar 16', 'Mar 17', 'Mar 18', 'Mar 19', 'Mar 20', 'Mar 21', 'Mar 22', 'Mar 23', 'Mar 24', 'Mar 25', 'Mar 26', 'Mar 27', 'Mar 28', 'Mar 29', 'Mar 30', 'Mar 31', 'Apr 01', 'Apr 02', 'Apr 03', 'Apr 04', 'Apr 05', 'Apr 06', 'Apr 07', 'Apr 08', 'Apr 09', 'Apr 10', 'Apr 11', 'Apr 12', 'Apr 13', 'Apr 14', 'Apr 15', 'Apr 16', 'Apr 17', 'Apr 18', 'Apr 19', 'Apr 20', 'Apr 21', 'Apr 22', 'Apr 23', 'Apr 24', 'Apr 25', 'Apr 26', 'Apr 27', 'Apr 28', 'Apr 29', 'Apr 30', 'May 01', 'May 02', 'May 03', 'May 04', 'May 05', 'May 06', 'May 07', 'May 08', 'May 09', 'May 10', 'May 11', 'May 12', 'May 13', 'May 14', 'May 15', 'May 16', 'May 17', 'May 18', 'May 19', 'May 20', 'May 21', 'May 22', 'May 23', 'May 24', 'May 25', 'May 26', 'May 27', 'May 28', 'May 29', 'May 30', 'May 31', 'Jun 01', 'Jun 02', 'Jun 03', 'Jun 04', 'Jun 05', 'Jun 06', 'Jun 07', 'Jun 08', 'Jun 09', 'Jun 10', 'Jun 11', 'Jun 12', 'Jun 13', 'Jun 14', 'Jun 15', 'Jun 16', 'Jun 17', 'Jun 18', 'Jun 19', 'Jun 20', 'Jun 21', 'Jun 22', 'Jun 23', 'Jun 24', 'Jun 25', 'Jun 26', 'Jun 27', 'Jun 28', 'Jun 29', 'Jun 30', 'Jul 01', 'Jul 02', 'Jul 03', 'Jul 04', 'Jul 05', 'Jul 06', 'Jul 07', 'Jul 08', 'Jul 09', 'Jul 10', 'Jul 11', 'Jul 12', 'Jul 13', 'Jul 14', 'Jul 15', 'Jul 16', 'Jul 17', 'Jul 18', 'Jul 19', 'Jul 20', 'Jul 21', 'Jul 22', 'Jul 23', 'Jul 24', 'Jul 25', 'Jul 26', 'Jul 27', 'Jul 28', 'Jul 29', 'Jul 30', 'Jul 31', 'Aug 01', 'Aug 02', 'Aug 03', 'Aug 04', 'Aug 05', 'Aug 06', 'Aug 07', 'Aug 08', 'Aug 09', 'Aug 10', 'Aug 11', 'Aug 12', 'Aug 13', 'Aug 14', 'Aug 15', 'Aug 16', 'Aug 17', 'Aug 18', 'Aug 19', 'Aug 20', 'Aug 21', 'Aug 22', 'Aug 23', 'Aug 24', 'Aug 25', 'Aug 26', 'Aug 27', 'Aug 28', 'Aug 29', 'Aug 30', 'Aug 31', 'Sep 01', 'Sep 02', 'Sep 03', 'Sep 04', 'Sep 05', 'Sep 06', 'Sep 07', 'Sep 08', 'Sep 09', 'Sep 10', 'Sep 11', 'Sep 12', 'Sep 13', 'Sep 14', 'Sep 15', 'Sep 16', 'Sep 17', 'Sep 18', 'Sep 19', 'Sep 20', 'Sep 21', 'Sep 22', 'Sep 23', 'Sep 24', 'Sep 25', 'Sep 26', 'Sep 27', 'Sep 28', 'Sep 29', 'Sep 30', 'Oct 01', 'Oct 02', 'Oct 03', 'Oct 04', 'Oct 05', 'Oct 06', 'Oct 07', 'Oct 08', 'Oct 09', 'Oct 10', 'Oct 11', 'Oct 12', 'Oct 13', 'Oct 14', 'Oct 15', 'Oct 16', 'Oct 17', 'Oct 18', 'Oct 19', 'Oct 20', 'Oct 21', 'Oct 22', 'Oct 23', 'Oct 24', 'Oct 25', 'Oct 26', 'Oct 27', 'Oct 28', 'Oct 29', 'Oct 30', 'Oct 31', 'Nov 01', 'Nov 02', 'Nov 03', 'Nov 04', 'Nov 05', 'Nov 06', 'Nov 07', 'Nov 08', 'Nov 09', 'Nov 10', 'Nov 11', 'Nov 12', 'Nov 13', 'Nov 14', 'Nov 15', 'Nov 16', 'Nov 17', 'Nov 18', 'Nov 19', 'Nov 20', 'Nov 21', 'Nov 22', 'Nov 23', 'Nov 24', 'Nov 25', 'Nov 26', 'Nov 27', 'Nov 28', 'Nov 29', 'Nov 30', 'Dec 01', 'Dec 02', 'Dec 03', 'Dec 04', 'Dec 05', 'Dec 06', 'Dec 07', 'Dec 08', 'Dec 09', 'Dec 10', 'Dec 11', 'Dec 12', 'Dec 13', 'Dec 14', 'Dec 15', 'Dec 16', 'Dec 17', 'Dec 18', 'Dec 19', 'Dec 20', 'Dec 21', 'Dec 22', 'Dec 23', 'Dec 24', 'Dec 25', 'Dec 26', 'Dec 27', 'Dec 28', 'Dec 29', 'Dec 30', 'Dec 31' ]
        }
    }
    tMod = 32 
    figure['layout'] = layout
    return figure
    
