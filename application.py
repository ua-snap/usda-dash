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
import urllib, json
from dash.dependencies import Input, Output, State

def get_max_days(datayear, community, threshold):
    day_counter = 0
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

# AWS Elastic Beanstalk looks for application by default,
# if this variable (application) isn't set you will get a WSGI error.
application = app.server

app.title = 'SNAP - USDA Garden Helper'

mapbox_access_token = os.environ['MAPBOX_ACCESS_TOKEN']
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
    #with urllib.request.urlopen('http://data.rcc-acis.org/StnData?sid=' + station + '&sdate=1950-01-01&edate=2019-03-15&elems=4') as url:
    #    acis_data = json.loads(url.read().decode())
    community = community + '_' + gcm
    df = pd.read_csv('data/' + community + '.csv')
    imperial_conversion_lu = {'temp':1.8,'precip':0.0393701}
    df[community] = df[community] * imperial_conversion_lu['temp'] + 32
    df['time'] = pd.to_datetime(df['time'])
    layout = {
        'title': 'Growing Season Length for ' + community,
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
            'autorange': 'reversed',
	    'tickformat': 'd'
	},
        'xaxis': { 
            'range': ['January 01', 'December 31'],
            'type': 'category',
	    'tickformat': '%m/%d',
	    'categoryarray': [ 'January 01', 'January 02', 'January 03', 'January 04', 'January 05', 'January 06', 'January 07', 'January 08', 'January 09', 'January 10', 'January 11', 'January 12', 'January 13', 'January 14', 'January 15', 'January 16', 'January 17', 'January 18', 'January 19', 'January 20', 'January 21', 'January 22', 'January 23', 'January 24', 'January 25', 'January 26', 'January 27', 'January 28', 'January 29', 'January 30', 'January 31', 'February 01', 'February 02', 'February 03', 'February 04', 'February 05', 'February 06', 'February 07', 'February 08', 'February 09', 'February 10', 'February 11', 'February 12', 'February 13', 'February 14', 'February 15', 'February 16', 'February 17', 'February 18', 'February 19', 'February 20', 'February 21', 'February 22', 'February 23', 'February 24', 'February 25', 'February 26', 'February 27', 'February 28', 'February 29', 'March 01', 'March 02', 'March 03', 'March 04', 'March 05', 'March 06', 'March 07', 'March 08', 'March 09', 'March 10', 'March 11', 'March 12', 'March 13', 'March 14', 'March 15', 'March 16', 'March 17', 'March 18', 'March 19', 'March 20', 'March 21', 'March 22', 'March 23', 'March 24', 'March 25', 'March 26', 'March 27', 'March 28', 'March 29', 'March 30', 'March 31', 'April 01', 'April 02', 'April 03', 'April 04', 'April 05', 'April 06', 'April 07', 'April 08', 'April 09', 'April 10', 'April 11', 'April 12', 'April 13', 'April 14', 'April 15', 'April 16', 'April 17', 'April 18', 'April 19', 'April 20', 'April 21', 'April 22', 'April 23', 'April 24', 'April 25', 'April 26', 'April 27', 'April 28', 'April 29', 'April 30', 'May 01', 'May 02', 'May 03', 'May 04', 'May 05', 'May 06', 'May 07', 'May 08', 'May 09', 'May 10', 'May 11', 'May 12', 'May 13', 'May 14', 'May 15', 'May 16', 'May 17', 'May 18', 'May 19', 'May 20', 'May 21', 'May 22', 'May 23', 'May 24', 'May 25', 'May 26', 'May 27', 'May 28', 'May 29', 'May 30', 'May 31', 'June 01', 'June 02', 'June 03', 'June 04', 'June 05', 'June 06', 'June 07', 'June 08', 'June 09', 'June 10', 'June 11', 'June 12', 'June 13', 'June 14', 'June 15', 'June 16', 'June 17', 'June 18', 'June 19', 'June 20', 'June 21', 'June 22', 'June 23', 'June 24', 'June 25', 'June 26', 'June 27', 'June 28', 'June 29', 'June 30', 'July 01', 'July 02', 'July 03', 'July 04', 'July 05', 'July 06', 'July 07', 'July 08', 'July 09', 'July 10', 'July 11', 'July 12', 'July 13', 'July 14', 'July 15', 'July 16', 'July 17', 'July 18', 'July 19', 'July 20', 'July 21', 'July 22', 'July 23', 'July 24', 'July 25', 'July 26', 'July 27', 'July 28', 'July 29', 'July 30', 'July 31', 'August 01', 'August 02', 'August 03', 'August 04', 'August 05', 'August 06', 'August 07', 'August 08', 'August 09', 'August 10', 'August 11', 'August 12', 'August 13', 'August 14', 'August 15', 'August 16', 'August 17', 'August 18', 'August 19', 'August 20', 'August 21', 'August 22', 'August 23', 'August 24', 'August 25', 'August 26', 'August 27', 'August 28', 'August 29', 'August 30', 'August 31', 'September 01', 'September 02', 'September 03', 'September 04', 'September 05', 'September 06', 'September 07', 'September 08', 'September 09', 'September 10', 'September 11', 'September 12', 'September 13', 'September 14', 'September 15', 'September 16', 'September 17', 'September 18', 'September 19', 'September 20', 'September 21', 'September 22', 'September 23', 'September 24', 'September 25', 'September 26', 'September 27', 'September 28', 'September 29', 'September 30', 'October 01', 'October 02', 'October 03', 'October 04', 'October 05', 'October 06', 'October 07', 'October 08', 'October 09', 'October 10', 'October 11', 'October 12', 'October 13', 'October 14', 'October 15', 'October 16', 'October 17', 'October 18', 'October 19', 'October 20', 'October 21', 'October 22', 'October 23', 'October 24', 'October 25', 'October 26', 'October 27', 'October 28', 'October 29', 'October 30', 'October 31', 'November 01', 'November 02', 'November 03', 'November 04', 'November 05', 'November 06', 'November 07', 'November 08', 'November 09', 'November 10', 'November 11', 'November 12', 'November 13', 'November 14', 'November 15', 'November 16', 'November 17', 'November 18', 'November 19', 'November 20', 'November 21', 'November 22', 'November 23', 'November 24', 'November 25', 'November 26', 'November 27', 'November 28', 'November 29', 'November 30', 'December 01', 'December 02', 'December 03', 'December 04', 'December 05', 'December 06', 'December 07', 'December 08', 'December 09', 'December 10', 'December 11', 'December 12', 'December 13', 'December 14', 'December 15', 'December 16', 'December 17', 'December 18', 'December 19', 'December 20', 'December 21', 'December 22', 'December 23', 'December 24', 'December 25', 'December 26', 'December 27', 'December 28', 'December 29', 'December 30', 'December 31' ]
        }
    }
    years = {}
    #for i in range (1971,2100):
    for i in range (1979,2101,5):
        years[i] = {}
    #years = { '1982': { 'color': '#ff0000' }, '1983': { 'color': '#ff0000' }, '1984': { 'color': '#ff0000' }, '1985': { 'color': '#ff0000' }, '2008': { 'color': '#ff0000' }, '2000': { 'color': '#ff0000' }, '2010': {'color': '#ff0000'}, '2020': {'color': '#ff0000'}, '2030': {'color': '#ff0000'}, '2040': {'color': '#ff0000'}, '2050': {'color': '#ff0000'}, '2060': {'color': '#ff0000'}, '2070': {'color': '#ff0000'}, '2080': {'color': '#ff0000'}, '2090': {'color': '#ff0000'} }
    figure = {}
    figure['data'] = []
    for key in sorted(years):
        df_annual = df[df['time'].dt.year == int(key)]
        df_annual['time'] = df_annual['time'].dt.strftime('%B %d')
        years[key] = get_max_days(df_annual, community, threshold)
        dates = [years[key]['startdate'], years[key]['enddate']]
        yrs = [str(key), str(key)]
        figure['data'].append({
            'x': dates,
            'y': yrs,
            #'text': ['Date of Thaw','Date of Freeze'],
            'name': str(years[key]['ndays']) + ' Days > ' + str(threshold) + ' ' + unit_lu['temp']['imperial'] + ', ' + str(key),
            'line': {
                'width': 8,
            },
            'marker': {
                'size': 25,
                'line': {
                    'width': 5,
                }
            }
        })
    '''
    for i in range(1980,2100,10):
        total_days = years[i]['ndays']
        total_days += years[i + 1]['ndays']
        total_days += years[i + 2]['ndays']
        total_days += years[i + 3]['ndays']
        total_days += years[i + 4]['ndays']
        total_days += years[i + 5]['ndays']
        total_days += years[i + 6]['ndays']
        total_days += years[i + 7]['ndays']
        total_days += years[i + 8]['ndays']
        total_days += years[i + 9]['ndays']
        average_days = total_days / 10
        print(str(i) + ' to ' + str(i + 10) + ' ' + str(average_days))
    '''
    tMod = 32 
    figure['layout'] = layout
    return figure
    

if __name__ == '__main__':
    application.run(debug=True, port=8080)
