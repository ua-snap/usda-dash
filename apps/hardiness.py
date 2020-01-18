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

layout = html.Div(
    children=[
        html.Div(
            className='section',
            children=[
                html.Div(
                    className='container',
                    children=[
			dcc.Markdown(
			"""
### Alaska Hardiness Maps
&nbsp;
			""",
                        className='content is-size-6'
			),
                        html.Div(
                            className='columns',
                            children=[
                                html.Div(
                                    children=[
                                        html.Img(src=path_prefix + 'assets/historical.png'),
                                    ]
                                ),
                                html.Div(
                                    children=[
                                        html.Img(src=path_prefix + 'assets/10-39.png'),
                                    ]
                                ),
                            ] 
                        ),
                        html.Div(
                            className='columns',
                            children=[
                                html.Div(
                                    children=[
                                        html.Img(src=path_prefix + 'assets/40-69.png'),
                                    ]
                                ),
                                html.Div(
                                    children=[
                                        html.Img(src=path_prefix + 'assets/70-99.png'),
                                    ]
                                ),
                            ]
                        ),
			dcc.Markdown(
			"""
##### Download Maps
[High Resolution Alaska Hardiness Maps](https://www.sciencebase.gov/catalog/item/5be4a2fbe4b0b3fc5cf8bd4a)
&nbsp;
			"""
			, 
                        className='content is-size-6'
                        ),
                        html.Div(id='location', className='container', style={ 'visibility': 'hidden' }),
                        dcc.Markdown(
                        """
### Hardiness Zones
##### About Hardiness
The USDA uses Plant Hardiness Zones as the standard by which growers can determine which plants are likely to thrive at a given location. Many seed manufacturers reference these zones.  Hardiness maps are based on the average annual minimum winter temperature.  These zones are only a rough guide.  Because they are based on winter temperatures, they are of greatest importance for perennials such as fruit trees or peonies.  It may make more sense to choose summer crops (annuals) based on our Growing Degree Day or Growing Season tools. Also, variations based on very fine scale differences in slope or elevation are too small to show up on these maps.
##### Future Hardiness Projections
These four maps represent current estimates of hardiness zones in Alaska, plus projections of how these zones may look in three future time periods, based on climate change models.  Looking at future zone maps can help guide long-term planting, and can also provide a starting point for discussions and further research about Alaska’s agricultural future.
 
[Find more information on USDA Hardiness Zones](https://planthardiness.ars.usda.gov/PHZMWeb/) 
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
