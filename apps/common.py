import os
import re
import pandas as pd
import xarray as xr
import dash_core_components as dcc
import dash_html_components as html

path_prefix = os.environ['REQUESTS_PATHNAME_PREFIX']

def calc_bias(community, gcm):
    comm_filename = re.sub('[^A-Za-z0-9]+', '', community) + '_' + gcm
    df = pd.read_csv('https://s3-us-west-2.amazonaws.com/community-logs-data/' + comm_filename + '.csv', index_col = 'time')
    dx = df.to_xarray()
    dx.rename({comm_filename: 'temp'},inplace=True)

    era_filename = re.sub('[^A-Za-z0-9]+', '', community) + '_ERA'
    ef = pd.read_csv('https://s3-us-west-2.amazonaws.com/community-logs-data/' + era_filename + '.csv', index_col = 'time')
    ex = ef.to_xarray()
    #print(ex)
    ex.rename({era_filename: 'temp'},inplace=True)
    dx['time'] = pd.to_datetime(dx['time'], format='%Y-%m-%d')
    ex['time'] = pd.to_datetime(ex['time'], format='%Y-%m-%d')
    dx_clip = dx.temp.loc['1980-01-01':'2010-12-31']
    ex_clip = ex.temp.loc['1980-01-01':'2010-12-31']
    dx_month_day_str = xr.DataArray(dx_clip.indexes['time'].strftime('%m-%d'), coords=dx_clip.coords, name='month_day_str')
    dx_mean = dx_clip.groupby(dx_month_day_str).mean()
    ex_month_day_str = xr.DataArray(ex_clip.indexes['time'].strftime('%m-%d'), coords=ex_clip.coords, name='month_day_str')
    ex_mean = ex_clip.groupby(ex_month_day_str).mean()
    bx = dx_mean - ex_mean
    return bx

def menu():
    menu = html.Div([
        #dcc.Link('Home   ', href='/'),
        dcc.Link('LOGS  | ', href='/logs'),
        dcc.Link('ANNUAL MIN  | ', href='/annual_min'),
        dcc.Link('CUMULATIVE GDD    ', href='/cumulative_gdd')
    ])
    return menu

def header():
    header = html.Div(
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
                                    ),
                                    menu()
                                ]
                            )
                        ]
                    )
                ]
            )
        ]
    )
    return header


def footer():
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
    return footer
