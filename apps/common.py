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
        #dcc.Link('Growing Season  | ', href='/logs'),
        #dcc.Link('Annual Minimum  | ', href='/annual_min'),
        #dcc.Link('Growing Degrees    ', href='/cumulative_gdd')
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
                                                'USDA Garden Helper',
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

            dcc.Markdown(
                """
Created by the Scenarios Network for Alaska and Arctic Planning, a climate change research group at the International Arctic Research Center at the University of Alaska Fairbanks (UAF). Many Alaska farmers and gardeners provided input, including experts from the UAF Georgeson Botanical Gardens, Spinach Creek Farm, Calypso Farm, and the Alaska Peony Growers Association.
Funding: USDA via the Alaska Climate Adaptation Science Center
<< contact us link >>
                """,
                className='content is-size-6'
            ),
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
UA is an AA/EO employer and educational institution and prohibits illegal discrimination against any individual. Notice of Nondiscrimination
                """,
                className='content is-size-6'
            ),
        ]
    )
    return footer
def infotext():
    infotext = html.Div(
            children=[
                dcc.Markdown(
                """
### Model Data
##### Where do these numbers come from?
Our models are based on global climate models that have been scaled down to the local level. Global models use information about how much our planet is expected to warm, how that extra heat is likely to be redistributed by the atmosphere and oceans, and how changes such as melting sea ice might cause feedback loops. We downscale these global models to account for finer landscape features like slope and elevation.
##### Why two models?
Climate models can only estimate conditions. Each global climate model is based on the best available data, but each makes different assumptions. By offering two models, we give you a chance to explore a model that produces bigger changes (GFDL model), and one that is more conservative (NCAR model). This allows you to think about different possible futures for agriculture in your area.

##### Why do results vary so much?
The models behind this tool provide estimates for squares of land 20 km (about 13 miles) on each side. Growing conditions can vary enormously across areas of this size, especially in hilly areas, where there’s a huge variety in slope and aspect (the direction in which a slope faces).

You may also notice trends—like future growing seasons getting longer—and random-seeming ups and downs. This is because models simulate the real world and its highly variable weather. We know that overall, our climate is warming, but long-term climate models can’t accurately predict the normal weather fluctuations that occur on short time scales. Gardeners should never forget to plan for variability!
##### Why we go so far into the future
Even the most ambitious Alaska growers are not planning their harvests for 2099. However, we include far-future modeled data in these tools because those who are more generally interested in climate change may want to see a longer-term picture. Also, a clearer picture of trends emerges at longer time scales.
##### What about other variables?
Here, you can explore future changes in growing season length, growing degree days, and coldest winter temperatures, all of which are important to crop growth and survival. We know that climate change will also affect rainfall, ground moisture, snow cover, and heat stress. These may be included in future versions of this tool, but for now, we’ve modeled an initial set of variables that growers told us were important. These variables were also relatively easy to work with in terms of time, data, and computing power.
                """
                ,
                className='content is-size-6'
                )
            ]
    )
    return infotext

