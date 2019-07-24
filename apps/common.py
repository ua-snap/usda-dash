import os
import re
import pandas as pd
import xarray as xr
import dash_core_components as dcc
import dash_html_components as html

path_prefix = os.environ['REQUESTS_PATHNAME_PREFIX']

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
